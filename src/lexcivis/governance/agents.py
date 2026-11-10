import hashlib
import re
from dataclasses import dataclass, fields

from ..answer import claimed_amounts
from ..llm import ChatModel, parse_json
from ..text import normalize, numbers

LAW = re.compile(r"\b(\d{4}-\d{3})\b")
ARTICLES = re.compile(r"\bart(?:icles?|s?\.)?\s*((?:\d+\s*(?:-|–|à|to|et|and|,)\s*)*\d+)", re.I)


@dataclass
class Situation:
    refused: bool = False
    held: bool = False
    stale: bool = False
    masked: bool = False
    hassaniya: bool = False
    unofficial_claim: bool = False
    data_abroad: bool = False
    rule_change: bool = False
    outage: bool = False
    access_request: bool = False
    coverage_gap: bool = False

    @property
    def flags(self) -> list[str]:
        return [f.name for f in fields(self) if getattr(self, f.name)]


def _mentions(text: str, words: list[str]) -> bool:
    t = normalize(text)
    return any(normalize(w) in t for w in words)


def situation(stage: dict, answers: list[dict], signals: dict) -> Situation:
    event = f"{stage.get('simulated', '')} {stage.get('title', '')}"
    official = set(numbers(" ".join(a["values"] for a in answers)))
    claims = set(numbers(" ".join(str(c) for c in stage.get("claim_numbers", [])))) | set(claimed_amounts(event)[1])
    claims |= {n for a in answers for n in a.get("claims", [])}
    fraud_words = _mentions(event, signals["unofficial_claim"])
    unofficial = bool(claims - official) or (fraud_words and not claims)
    rule_change = _mentions(event, signals["rule_change"]) and not unofficial
    return Situation(
        refused=any(a["status"] == "refused" for a in answers),
        held=any(a["status"] == "held" for a in answers),
        stale=rule_change and any(a["status"] != "refused" for a in answers),
        masked=any(a["masked"] for a in answers),
        hassaniya=any(a["hassaniya"] for a in answers),
        unofficial_claim=unofficial,
        data_abroad=_mentions(event, signals["data_abroad"]),
        rule_change=rule_change,
        outage=_mentions(event, signals["outage"]),
        access_request=_mentions(event, signals["access_request"]),
        coverage_gap=any(a["status"] == "refused" and not a.get("claims") for a in answers),
    )


def rule_decision(agent_id: str, s: Situation, playbook: dict) -> dict:
    actions, seen = [], set()
    for step in playbook.get(agent_id, []):
        if getattr(s, step["when"]) and step["action"] not in seen:
            seen.add(step["action"])
            actions.append({"action": step["action"], "target": step["target"], "reason": step["when"],
                            "legal_basis": [f"Law {b}" if b[:4].isdigit() else b for b in step["basis"]]})
    return {"assessment": f"Playbook decision on: {', '.join(s.flags) or 'no signal'}.", "actions": actions,
            "message": "", "author": "rules"}


def cited_articles(basis: list[str]) -> set[tuple[str, str]]:
    out = set()
    for b in basis:
        laws = LAW.findall(b) or ["2017-020"]
        for group in ARTICLES.findall(b):
            nums = [int(n) for n in re.findall(r"\d+", group)]
            if re.search(r"\d\s*(?:-|–|à|to)\s*\d", group) and len(nums) == 2 and nums[0] < nums[1] <= nums[0] + 30:
                nums = list(range(nums[0], nums[1] + 1))
            out |= {(law, str(n)) for law in laws for n in nums}
    return out


def allowed_slice(agent: dict) -> tuple[set[tuple[str, str]], set[str]]:
    articles = cited_articles(agent["law"])
    whole_laws = {law for ref in agent["law"] if not ARTICLES.search(ref) for law in LAW.findall(ref)}
    return articles, whole_laws


def check_basis(actions: list[dict], agent: dict) -> list[dict]:
    articles, whole_laws = allowed_slice(agent)
    out = []
    for a in actions:
        basis = a.get("legal_basis") or []
        basis = [basis] if isinstance(basis, str) else [str(b) for b in basis]
        unknown = sorted(f"{law} art. {n}" for law, n in cited_articles(basis) - articles if law not in whole_laws)
        out.append({**a, "legal_basis": basis, "basis_outside_slice": unknown})
    return out


def _law_text(refs: list[str], law: dict) -> str:
    out = []
    for ref in refs:
        m = re.match(r"2017-020 art\. (\d+)", ref)
        out.append(f"- Law 2017-020, art. {m[1]}: {law[m[1]][:700]}" if m and m[1] in law else f"- {ref}")
    return "\n".join(out)


def _prompt(agent: dict, stage: dict, answers: list[dict], board: list[dict], law: dict) -> str:
    seen = "\n".join(f"* Q ({a['lang']}): {a['query']}\n  status: {a['status']}\n  reply: {a['text'][:600]}"
                     for a in answers) or "(no citizen question in this stage)"
    others = "\n".join(f"* {b['agent']}: {b['message']} | {[(x['action'], x['status']) for x in b['actions']]}"
                       for b in board) or "(none yet)"
    return (f"You are \"{agent['name']}\" in a public-sector AI governance sandbox (a simulation).\n"
            f"Role: {agent['role']}\nActions you MAY propose (exact names only): {agent['may']}\n"
            f"You must NOT: {agent['must_not']}\nYour legal texts (cite only these, never invent law):\n"
            f"{_law_text(agent['law'], law)}\n\nSTAGE {stage['id']} (day {stage['day']}): {stage['title']}\n"
            f"Situation: {stage['simulated']}\nCitizen assistant:\n{seen}\nOther institutions:\n{others}\n\n"
            "Decide what your institution does now, inside your mandate. Say 'for expert review' when unsure.\n"
            'Return ONLY JSON: {"assessment": "2-3 sentences", "actions": [{"action": "...", "target": "...", '
            '"reason": "...", "legal_basis": ["..."]}], "message": "one sentence to the other institutions"}')


SYSTEM = "You are a careful public-administration agent. You answer with one JSON object only."


def llm_decision(model: ChatModel, agent: dict, stage: dict, answers: list[dict], board: list[dict],
                 law: dict) -> tuple[dict | None, dict]:
    prompt = _prompt(agent, stage, answers, board, law)
    trace = {"model": model.name, "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(), "raw": []}
    for suffix in ("", "\nReturn valid JSON only."):
        try:
            raw = model.complete(SYSTEM, prompt + suffix, max_tokens=900)
        except Exception as exc:
            trace["error"] = type(exc).__name__
            return None, trace
        trace["raw"].append(raw[:4000])
        d = parse_json(raw)
        if d and isinstance(d.get("actions"), list):
            d["actions"] = [a for a in d["actions"] if isinstance(a, dict)]
            d["author"] = f"llm:{model.name}"
            return d, trace
    trace["error"] = "invalid JSON"
    return None, trace


def decide(agent_id: str, cfg: dict, stage: dict, answers: list[dict], board: list[dict], law: dict,
           s: Situation, model: ChatModel | None) -> dict:
    agent = cfg["agents"][agent_id]
    d, trace = llm_decision(model, agent, stage, answers, board, law) if model else (None, {})
    if d is None:
        d = rule_decision(agent_id, s, cfg["playbook"])
        if trace:
            d["author"] = f"rules (LLM failed: {trace.get('error', 'unknown')})"
    out = {"agent": agent_id, "assessment": str(d.get("assessment", "")), "message": str(d.get("message", "")),
           "actions": check_basis(d["actions"], agent), "author": d["author"]}
    if trace:
        out["llm"] = trace
    return out

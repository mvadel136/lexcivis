import json
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timezone
from importlib import resources
from pathlib import Path

import yaml

from ..answer import Composer
from ..llm import ChatModel
from .agents import decide, situation
from .brief import write_brief
from .guard import Guard
from .ledger import Ledger, records, verify
from .seal import seal

RUN_ID = r"^\d{8}T\d{6}Z-[0-9a-f]{6}$"


def resource(name: str) -> str:
    return resources.files("lexcivis.governance.resources").joinpath(name).read_text(encoding="utf-8")


def load_config() -> dict:
    cfg = yaml.safe_load(resource("agents.yaml"))
    cfg.update(yaml.safe_load(resource("playbook.yaml")))
    cfg["stages"] = yaml.safe_load(resource("events.yaml"))["stages"]
    gaps = yaml.safe_load(resource("gaps.yaml"))
    cfg["gaps"], cfg["dimensions"] = gaps["gaps"], gaps["dimensions"]
    cfg["law"] = json.loads(resource("law_2017_020.json"))["articles"]
    return cfg


@dataclass
class StageResult:
    stage: dict
    answers: list = field(default_factory=list)
    board: list = field(default_factory=list)

    @property
    def pending(self) -> list[dict]:
        return [{**a, "agent": b["agent"], "seq": b["seq"]} for b in self.board for a in b["actions"]
                if a["status"] == "AWAITING_HUMAN"]


@dataclass
class Run:
    directory: Path
    results: list
    chain_ok: bool
    records: int


def injected_stage(text: str, question: str, cfg: dict) -> dict:
    return {"id": "S7", "day": 40, "title": "Live event", "simulated": text,
            "questions": [{"lang": "", "text": question}] if question else [], "agents": list(cfg["agents"])}


def new_run_dir(out_dir: str | Path) -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    directory = Path(out_dir) / f"{stamp}-{secrets.token_hex(3)}"
    directory.mkdir(parents=True, exist_ok=False)
    return directory


def run_exercise(composer: Composer, out_dir: str | Path, model: ChatModel | None = None,
                 only: list[str] | None = None, inject: str = "", inject_question: str = "",
                 provenance: dict | None = None, signing: tuple[Path, str] | None = None) -> Run:
    cfg = load_config()
    stages = [s for s in cfg["stages"] if not only or s["id"] in only]
    if inject:
        stages.append(injected_stage(inject, inject_question, cfg))
    directory = new_run_dir(out_dir)
    ledger, guard = Ledger(directory / "ledger.jsonl"), Guard(cfg)
    ledger.append("run_start", "ORCHESTRATOR", {"stages": [s["id"] for s in stages],
                                                "agents_backend": model.name if model else "rules",
                                                **(provenance or {})})
    results = [_run_stage(stage, composer, ledger, guard, cfg, model) for stage in stages]
    if signing and Path(signing[0]).exists():
        seal(ledger.path, *signing)
    ok, n, _ = verify(ledger.path)
    (directory / "results.json").write_text(json.dumps(
        [{"stage": r.stage, "answers": r.answers, "board": r.board} for r in results], ensure_ascii=False, indent=1),
        encoding="utf-8")
    write_brief(results, directory / "case_brief.md", ok, n, ledger.prev)
    return Run(directory, results, ok, n)


def _scripted(entries: list[dict], guard: Guard, done: set, ledger: Ledger, stage: dict) -> list[dict]:
    out = []
    for entry in entries:
        action = {k: v for k, v in entry.items() if k != "agent"}
        d = {"agent": entry["agent"], "assessment": "Scripted adversarial proposal.", "message": "",
             "actions": guard.review(entry["agent"], [action], done), "author": "script"}
        d["seq"] = ledger.append("agent_decision", entry["agent"], d, stage["id"], stage["day"])["seq"]
        out.append(d)
    return out


def _run_stage(stage: dict, composer: Composer, ledger: Ledger, guard: Guard, cfg: dict,
               model: ChatModel | None) -> StageResult:
    result = StageResult(stage)
    ledger.append("stage_start", "ORCHESTRATOR", {"title": stage["title"], "situation": stage["simulated"]},
                  stage["id"], stage["day"])
    for q in stage.get("questions", []):
        a = composer.answer(q["text"], q.get("lang") or None)
        ledger.append("citizen_question", "CITIZEN", {"text": a.query, "masked": a.masked}, stage["id"], stage["day"])
        record = {**a.to_dict(), "values": a.values}
        ledger.append("assistant_answer", "ASSISTANT", record, stage["id"], stage["day"])
        result.answers.append(record)
    s = situation(stage, result.answers, cfg["signals"])
    ledger.append("situation", "ORCHESTRATOR", {"signals": s.flags}, stage["id"], stage["day"])
    done: set[str] = set()
    result.board += _scripted(stage.get("scripted_before", []), guard, done, ledger, stage)
    for agent_id in stage.get("agents", []):
        d = decide(agent_id, cfg, stage, result.answers, result.board, cfg["law"], s, model)
        d["actions"] = guard.review(agent_id, d["actions"], done)
        d["seq"] = ledger.append("agent_decision", agent_id, d, stage["id"], stage["day"])["seq"]
        result.board.append(d)
    result.board += _scripted(stage.get("scripted_after", []), guard, done, ledger, stage)
    ledger.append("stage_end", "ORCHESTRATOR", {"awaiting_human": len(result.pending)}, stage["id"], stage["day"])
    return result


def record_decision(ledger_path: str | Path, seq: int, action: str, decision: str, by: str, note: str = "",
                    signing: tuple[Path, str] | None = None) -> dict:
    if decision not in ("approve", "reject"):
        raise ValueError("decision must be approve or reject")
    if not by.strip():
        raise ValueError("a named person is required")
    target = next((r for r in records(ledger_path) if r["seq"] == seq and r["kind"] == "agent_decision"), None)
    if not target:
        raise ValueError(f"no agent decision at seq {seq}")
    pending = [a for a in target["payload"]["actions"] if a["action"] == action and a["status"] == "AWAITING_HUMAN"]
    if not pending:
        raise ValueError(f"'{action}' at seq {seq} is not waiting for a human")
    ledger = Ledger.resume(ledger_path)
    record = ledger.append("human_decision", by.strip(), {"decision_seq": seq, "agent": target["actor"], "action": action,
                                                           "decision": decision, "note": note}, target["stage"],
                           target["sim_day"])
    if signing and Path(signing[0]).exists():
        seal(ledger_path, *signing)
    return record

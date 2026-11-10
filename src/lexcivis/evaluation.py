import json
import statistics
import time
from collections import defaultdict
from pathlib import Path

from .answer import Composer
from .catalog import Field
from .quality import duplicate_titles


def _keys(item: dict) -> set[str]:
    if "keys" in item:
        return set(item["keys"])
    return {f"fr{item['expected_fr_id']}"}


def _verbatim(answer, catalog) -> bool:
    p = catalog.get(answer.procedure_key)
    if answer.status == "refused" or not p:
        return False
    sources = {r.get(Field(i.field)) for r in p.records for i in answer.items}
    for i in answer.items:
        if i.held:
            if i.fr_value not in sources or i.ar_value not in sources:
                return False
        elif i.source_lang and i.value not in sources:
            return False
    return True


def twins(catalog) -> dict[str, set[str]]:
    out = {}
    for group in duplicate_titles(catalog):
        for key in group:
            out[key] = set(group)
    return out


def run_set(composer: Composer, catalog, items: list[dict], expect_refusal: bool = False) -> dict:
    by_lang = defaultdict(lambda: defaultdict(int))
    same = twins(catalog)
    latencies, failures, outcomes = [], [], []
    for item in items:
        t0 = time.perf_counter()
        a = composer.answer(item["query"], None if item.get("lang") == "hassaniya" else item.get("lang"))
        latencies.append(time.perf_counter() - t0)
        lang = item.get("lang", "?")
        outcomes.append({"got": a.procedure_key, "intent": a.intent, "status": a.status})
        s = by_lang[lang]
        s["n"] += 1
        if expect_refusal:
            s["refused"] += a.status == "refused"
            if a.status != "refused":
                failures.append({"query": item["query"], "got": a.title})
            continue
        ranked = [a.procedure_key] + [x["key"] for x in a.alternatives] if a.status != "refused" else []
        expected = _keys(item)
        top1 = bool(ranked) and ranked[0] in expected
        candidates = [c["key"] for c in a.trace.get("candidates", [])]
        s["recall@1"] += top1
        s["recall@1_twins"] += bool(ranked) and ranked[0] in set().union(*(same.get(k, {k}) for k in expected))
        s["recall@3"] += bool(expected & set(candidates[:3]))
        s["refused"] += a.status == "refused"
        s["verbatim"] += _verbatim(a, catalog)
        s["answered"] += a.status != "refused"
        if "field" in item:
            field_ok = a.intent == item["field"]
            s["field"] += field_ok
            s["end_to_end"] += field_ok and top1
        if not top1 or ("field" in item and a.intent != item["field"]):
            failures.append({"query": item["query"], "expected": sorted(expected), "got": a.procedure_key,
                             "got_title": a.title, "field": item.get("field"), "intent": a.intent, "status": a.status})
    total = defaultdict(int)
    for s in by_lang.values():
        for k, v in s.items():
            total[k] += v
    return {"by_lang": {k: dict(v) for k, v in by_lang.items()}, "total": dict(total),
            "latency_p50_s": round(statistics.median(latencies), 2),
            "latency_p95_s": round(sorted(latencies)[int(0.95 * (len(latencies) - 1))], 2), "failures": failures,
            "outcomes": outcomes}


def _load(directory: Path, name: str) -> list[dict]:
    return json.loads((directory / name).read_text(encoding="utf-8"))


def evaluate(composer: Composer, catalog, eval_dir: str | Path) -> dict:
    d = Path(eval_dir)

    def load(name: str) -> list[dict]:
        return _load(d, name)

    return {
        "procedures_50": run_set(composer, catalog, load("procedures_50.json")),
        "field_questions_55": run_set(composer, catalog, load("field_questions.json")),
        "must_refuse_10": run_set(composer, catalog, load("must_refuse_10.json"), expect_refusal=True),
        "must_refuse_holdout_20": run_set(composer, catalog, load("must_refuse_holdout.json"), expect_refusal=True),
    }


def summary_table(results: dict) -> str:
    rows = ["| Set | n | Recall@1 | Recall@1 (twins) | Recall@3 | Field | End-to-end | Refused | p50 s |",
            "|---|---|---|---|---|---|---|---|---|"]
    for name, r in results.items():
        t = r["total"]
        n = t.get("n", 0)

        def pct(k: str) -> str:
            return f"{100 * t.get(k, 0) / n:.0f}%" if n and k in t else "–"

        rows.append(f"| {name} | {n} | {pct('recall@1')} | {pct('recall@1_twins')} | {pct('recall@3')} | {pct('field')} | {pct('end_to_end')} | "
                    f"{t.get('refused', 0)} | {r['latency_p50_s']} |")
    return "\n".join(rows)


def intent_check(results: dict, targets: dict) -> list[dict]:
    out = []
    for key, target in targets.items():
        name, metric = key.rsplit(".", 1)
        r = results.get(name)
        if not r:
            out.append({"target": key, "goal": target, "value": None, "met": None})
            continue
        if "summary" in r:
            value = r["summary"][metric]["value"]
        else:
            t = r["total"]
            value = t.get(metric, 0) / t["n"] if t.get("n") else 0
        out.append({"target": key, "goal": target, "value": round(value, 3), "met": value >= target})
    return out

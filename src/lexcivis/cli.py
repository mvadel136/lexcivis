import argparse
import json
import sys
from pathlib import Path

from .settings import ROOT, Settings


def _build(args) -> None:
    from .engine import build_artifacts

    print(json.dumps(build_artifacts(Settings())))


def _ask(args) -> None:
    from .engine import load_engine

    a = load_engine().composer.answer(" ".join(args.question), args.lang)
    print(json.dumps(a.to_dict(), ensure_ascii=False, indent=1) if args.json else a.text)


def _quality(args) -> None:
    from .catalog import Catalog
    from .quality import Verdicts, audit

    s = Settings()
    report = audit(Catalog.load(s.data_path), Verdicts.load(s.verdicts_path)).to_dict()
    if not args.full:
        report.pop("conflicts")
    print(json.dumps(report, ensure_ascii=False, indent=1))


def _profile(args) -> None:
    from .catalog import Catalog
    from .profile import write_profile
    from .quality import Verdicts

    s = Settings()
    report = write_profile(Catalog.load(s.data_path), Verdicts.load(s.verdicts_path), args.out)
    keys = ("procedures", "fee_kinds", "delay_kinds", "with_legal_basis", "generic_contact_only", "related_links", "completeness_mean")
    print(json.dumps({k: report[k] for k in keys}, ensure_ascii=False, indent=1))


def _library(args) -> None:
    from .documents import build_library

    s = Settings()
    print(json.dumps(build_library(s.data_path, args.source, s.library_path)))


def _inputdocs(args) -> None:
    from .inputdocs import export_inputdocs

    s = Settings()
    law = ROOT / "src" / "lexcivis" / "governance" / "resources" / "law_2017_020.json"
    print(json.dumps(export_inputdocs(s.data_path, s.library_path, law, args.out)))


def _evaluate(args) -> None:
    from .engine import load_engine
    from .evaluation import evaluate, summary_table

    from .engine import ml_intent
    from .evaluation import intent_check

    e = load_engine()
    results = evaluate(e.composer, e.catalog, args.eval_dir)
    bench = Path(args.out).parent / "benchmark_v2.json"
    if bench.exists():
        results["benchmark_v2"] = {"summary": json.loads(bench.read_text(encoding="utf-8"))["summary"]}
    results["intent_check"] = intent_check(results, ml_intent()["targets"])
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")
    print(summary_table({k: v for k, v in results.items() if "total" in v}))
    for c in results["intent_check"]:
        print(f"{'MET ' if c['met'] else 'MISS' if c['met'] is False else '----'} {c['target']}: {c['value']} (goal {c['goal']})")


def _benchmark(args) -> None:
    from .benchmark import bootstrap, generate, write
    from .engine import load_engine
    from .evaluation import run_set

    e = load_engine()
    if Path(args.questions).exists() and not args.regenerate:
        items = json.loads(Path(args.questions).read_text(encoding="utf-8"))
    else:
        items = generate(e.catalog, args.templates, args.per_cell, args.seed)
        write(items, args.questions)
    result = run_set(e.composer, e.catalog, items)
    rows = {}
    for name, test in (("procedure@1", lambda i, f: f["got"] in i["keys"]), ("field", lambda i, f: f["intent"] == i["field"])):
        rows[name] = bootstrap([test(i, o) for i, o in zip(items, result["outcomes"])])
    rows["end_to_end"] = bootstrap([o["got"] in i["keys"] and o["intent"] == i["field"] for i, o in zip(items, result["outcomes"])])
    result["summary"] = {k: {"value": round(v[0], 3), "ci95": [round(v[1], 3), round(v[2], 3)]} for k, v in rows.items()}
    Path(args.out).write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(result["summary"], indent=1))


def _exercise(args) -> None:
    from .engine import load_engine
    from .governance.exercise import run_exercise
    from .llm import chat_model

    e = load_engine()
    model = chat_model(e.settings) if args.llm else None
    run = run_exercise(e.composer, e.settings.runs, model, args.stages.split(",") if args.stages else None,
                       args.inject, args.inject_question, e.provenance, (e.settings.signing_key, e.settings.signer))
    print(f"{run.directory} · ledger {'verified' if run.chain_ok else 'BROKEN'} ({run.records} records)")
    for r in run.results:
        for p in r.pending:
            print(f"  waiting: {r.stage['id']} seq {p['seq']} {p['agent']} {p['action']}")


def _approve(args) -> None:
    from .governance.exercise import record_decision

    ledger = Path(args.run) / "ledger.jsonl" if Path(args.run).is_dir() else Settings().runs / args.run / "ledger.jsonl"
    s = Settings()
    record = record_decision(ledger, args.seq, args.action, args.decision, args.by, args.note, (s.signing_key, s.signer))
    print(f"recorded seq {record['seq']} · {args.decision} by {args.by} · {record['hash'][:16]}")


def _verify(args) -> None:
    from .governance.ledger import verify
    from .governance.seal import check

    s = Settings()
    ok, n, bad = verify(args.ledger)
    trusted = s.trusted_key.read_text(encoding="utf-8") if s.trusted_key.exists() else None
    sealed, detail = check(args.ledger, trusted)
    print(f"{'CHAIN OK' if ok else f'CHAIN BROKEN at seq {bad}'}: {n} records · seal: {detail}")
    sys.exit(0 if ok and sealed else 1)


def _keygen(args) -> None:
    from .governance.seal import generate

    s = Settings()
    if s.signing_key.exists() and not args.force:
        sys.exit(f"{s.signing_key} exists; use --force to replace it")
    print(generate(s.signing_key, s.trusted_key))


def _serve(args) -> None:
    import uvicorn

    from .api import create_app

    uvicorn.run(create_app(), host=args.host, port=args.port)


def main() -> None:
    p = argparse.ArgumentParser(prog="lexcivis")
    sub = p.add_subparsers(required=True)
    sub.add_parser("build").set_defaults(fn=_build)
    a = sub.add_parser("ask")
    a.add_argument("question", nargs="+")
    a.add_argument("--lang", choices=["fr", "ar"])
    a.add_argument("--json", action="store_true")
    a.set_defaults(fn=_ask)
    q = sub.add_parser("quality")
    q.add_argument("--full", action="store_true")
    q.set_defaults(fn=_quality)
    pr = sub.add_parser("profile")
    pr.add_argument("--out", default=str(ROOT / "data" / "derived"))
    pr.set_defaults(fn=_profile)
    lb = sub.add_parser("library")
    lb.add_argument("source")
    lb.set_defaults(fn=_library)
    ix = sub.add_parser("inputdocs")
    ix.add_argument("out")
    ix.set_defaults(fn=_inputdocs)
    ev = sub.add_parser("evaluate")
    ev.add_argument("--eval-dir", default=str(ROOT / "data" / "eval"))
    ev.add_argument("--out", default=str(ROOT / "reports" / "evaluation.json"))
    ev.set_defaults(fn=_evaluate)
    b = sub.add_parser("benchmark")
    b.add_argument("--templates", default=str(ROOT / "data" / "eval" / "benchmark_v2_templates.yaml"))
    b.add_argument("--questions", default=str(ROOT / "data" / "eval" / "benchmark_v2_200.json"))
    b.add_argument("--per-cell", type=int, default=20)
    b.add_argument("--seed", type=int, default=11)
    b.add_argument("--regenerate", action="store_true")
    b.add_argument("--out", default=str(ROOT / "reports" / "benchmark_v2.json"))
    b.set_defaults(fn=_benchmark)
    x = sub.add_parser("exercise")
    x.add_argument("--stages", default="")
    x.add_argument("--inject", default="")
    x.add_argument("--inject-question", default="")
    x.add_argument("--llm", action="store_true")
    x.set_defaults(fn=_exercise)
    ap = sub.add_parser("approve")
    ap.add_argument("run")
    ap.add_argument("seq", type=int)
    ap.add_argument("action")
    ap.add_argument("--by", required=True)
    ap.add_argument("--decision", choices=["approve", "reject"], default="approve")
    ap.add_argument("--note", default="")
    ap.set_defaults(fn=_approve)
    k = sub.add_parser("keygen")
    k.add_argument("--force", action="store_true")
    k.set_defaults(fn=_keygen)
    v = sub.add_parser("verify")
    v.add_argument("ledger")
    v.set_defaults(fn=_verify)
    s = sub.add_parser("serve")
    s.add_argument("--host", default="127.0.0.1")
    s.add_argument("--port", type=int, default=8080)
    s.set_defaults(fn=_serve)
    args = p.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()

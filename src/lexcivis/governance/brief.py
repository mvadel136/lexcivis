from pathlib import Path

MARK = {"ALLOWED": "allowed", "AWAITING_HUMAN": "awaiting a named human",
        "BLOCKED_MANDATE": "BLOCKED (outside mandate)", "BLOCKED_ORDER": "BLOCKED (legal order)"}


def _action_line(x: dict) -> str:
    basis = ", ".join(x.get("legal_basis") or []) or "no legal basis given"
    rule = f" — {x['rule']}" if x.get("rule") else ""
    outside = f" ⚠ cites outside its legal slice: {', '.join(x['basis_outside_slice'])}" if x.get("basis_outside_slice") else ""
    return f"- {MARK.get(x['status'], x['status'])}: `{x.get('action')}` → {x.get('target', '')} ({basis}){rule}{outside}"


def write_brief(results: list, path: str | Path, chain_ok: bool, records: int, head: str) -> None:
    lines = ["# LexCivis case brief", "",
             f"Ledger: {records} records, hash chain {'verified' if chain_ok else 'BROKEN'}, head `{head[:16]}`.", ""]
    for r in results:
        s = r.stage
        lines += [f"## {s['id']} · day {s['day']} · {s['title']}", "", f"Situation: {s['simulated']}", ""]
        for a in r.answers:
            lines += [f"**Citizen:** {a['query']}", "", f"**Status:** {a['status']} · procedure: {a['title'] or '–'}", "",
                      "```", a["text"], "```", ""]
        for b in r.board:
            lines.append(f"**{b['agent']}** ({b['author']}, seq {b['seq']}): {b['assessment']}")
            lines += [_action_line(x) for x in b["actions"]]
            lines.append("")
        if r.pending:
            lines += ["**Waiting for a named human** (`lexcivis approve <run> <seq> <action> --by NAME`):",
                      *[f"- [ ] seq {p['seq']} · {p['agent']}: `{p['action']}`" for p in r.pending], ""]
    Path(path).write_text("\n".join(lines), encoding="utf-8")

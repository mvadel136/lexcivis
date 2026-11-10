import json

import pytest

from lexcivis.governance.exercise import load_config, record_decision, run_exercise
from lexcivis.governance.guard import Guard
from lexcivis.governance.ledger import Ledger, verify


def guard():
    return Guard(load_config())


def statuses(result):
    return [(b["agent"], a["action"], a["status"]) for b in result.board for a in b["actions"]]


def test_training_on_logs_is_outside_mandate():
    assert guard().review("CLOUD_HOST", [{"action": "use_logs_for_training"}], set())[0]["status"] == "BLOCKED_MANDATE"


def test_transfer_needs_notification_and_approved_conditions():
    g = guard()
    done = set()
    assert g.review("OPERATOR", [{"action": "transfer_logs_abroad"}], done)[0]["status"] == "BLOCKED_ORDER"
    assert g.review("DATA_PROTECTION", [{"action": "require_notification"}], done)[0]["status"] == "ALLOWED"
    assert g.review("OPERATOR", [{"action": "transfer_logs_abroad"}], done)[0]["status"] == "BLOCKED_ORDER"
    assert g.review("DATA_PROTECTION", [{"action": "set_transfer_conditions"}], done)[0]["status"] == "BLOCKED_ORDER"
    assert g.review("OPERATOR", [{"action": "notify_authority"}], done)[0]["status"] == "ALLOWED"
    assert g.review("DATA_PROTECTION", [{"action": "set_transfer_conditions"}], done)[0]["status"] == "AWAITING_HUMAN"
    assert g.review("OPERATOR", [{"action": "transfer_logs_abroad"}], done)[0]["status"] == "BLOCKED_ORDER"
    done.add("DATA_PROTECTION:set_transfer_conditions")
    assert g.review("OPERATOR", [{"action": "transfer_logs_abroad"}], done)[0]["status"] == "AWAITING_HUMAN"


def test_public_actions_wait_for_a_human():
    for action in ("publish_notice_draft", "show_warning_to_users", "pause_feature"):
        assert guard().review("OPERATOR", [{"action": action}], set())[0]["status"] == "AWAITING_HUMAN"


def test_ledger_detects_tampering_and_truncation(tmp_path):
    path = tmp_path / "ledger.jsonl"
    ledger = Ledger(path)
    for i in range(3):
        ledger.append("event", "test", {"i": i})
    assert verify(path) == (True, 3, None)
    lines = path.read_text().splitlines()
    path.write_text("\n".join(lines[:2]) + "\n")
    assert not verify(path)[0]
    record = json.loads(lines[1])
    record["payload"]["i"] = 42
    path.write_text("\n".join([lines[0], json.dumps(record), lines[2]]) + "\n")
    assert verify(path) == (False, 1, 1)


def test_full_exercise_with_rule_agents(composer, tmp_path):
    run = run_exercise(composer, tmp_path)
    assert run.chain_ok and run.records > 30
    by_id = {r.stage["id"]: r for r in run.results}
    assert any(a["status"] == "held" for a in by_id["S2"].answers)
    s5 = statuses(by_id["S5"])
    assert ("CLOUD_HOST", "use_logs_for_training", "BLOCKED_MANDATE") in s5
    assert [st for _, a, st in s5 if a == "transfer_logs_abroad"] == ["BLOCKED_ORDER", "BLOCKED_ORDER"]
    s6 = statuses(by_id["S6"])
    assert any(a == "request_takedown" for _, a, _ in s6)
    assert not any(a in ("request_record_update", "add_language_gap") for _, a, _ in s6)
    assert (run.directory / "case_brief.md").exists()


def test_runs_never_share_a_ledger(composer, tmp_path):
    a = run_exercise(composer, tmp_path, only=["S1"])
    b = run_exercise(composer, tmp_path, only=["S1"])
    assert a.directory != b.directory and a.chain_ok and b.chain_ok


def test_access_request_signal(composer, tmp_path):
    run = run_exercise(composer, tmp_path, only=["S1"], inject="La police demande les journaux avec les numéros NNI sans réquisition du tribunal")
    actions = {(agent, a) for agent, a, _ in statuses(run.results[-1])}
    assert ("CLOUD_HOST", "request_confirmation") in actions and ("DATA_PROTECTION", "request_information") in actions


def test_seal_detects_a_rewritten_chain(composer, tmp_path):
    from lexcivis.governance.ledger import digest, records
    from lexcivis.governance.seal import check, generate

    key, pub = tmp_path / "k.pem", tmp_path / "k.pub"
    trusted = generate(key, pub)
    run = run_exercise(composer, tmp_path / "runs", only=["S6"], signing=(key, "Authority"))
    ledger = run.directory / "ledger.jsonl"
    assert check(ledger, trusted)[0]
    rows = records(ledger)
    rows[3]["payload"] = {"forged": True}
    prev = rows[2]["hash"]
    for r in rows[3:]:
        r["prev"] = prev
        r["hash"] = digest(r)
        prev = r["hash"]
    ledger.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))
    ledger.with_suffix(".head").write_text(f"{len(rows)} {prev}\n")
    assert verify(ledger)[0]
    assert check(ledger, trusted) == (False, "sealed head does not match the ledger")


def test_live_injection_works_without_llm(composer, tmp_path):
    run = run_exercise(composer, tmp_path, only=["S1"], inject="Un faux SMS annonce un nouveau tarif de 9000 MRU pour le passeport")
    s7 = run.results[-1]
    assert s7.stage["id"] == "S7"
    actions = {a for _, a, _ in statuses(s7)}
    assert {"open_incident", "request_takedown", "confirm_authoritative_value"} <= actions


def test_human_decision_is_chained(composer, tmp_path):
    run = run_exercise(composer, tmp_path, only=["S6"])
    pending = run.results[0].pending[0]
    ledger = run.directory / "ledger.jsonl"
    record = record_decision(ledger, pending["seq"], pending["action"], "approve", "Duty officer")
    assert record["kind"] == "human_decision" and verify(ledger)[0]
    with pytest.raises(ValueError):
        record_decision(ledger, pending["seq"], "use_logs_for_training", "approve", "Duty officer")
    with pytest.raises(ValueError):
        record_decision(ledger, pending["seq"], pending["action"], "approve", " ")

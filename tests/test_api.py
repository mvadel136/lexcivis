import pytest
from fastapi.testclient import TestClient

from lexcivis.api import create_app
from lexcivis.engine import Engine
from lexcivis.settings import Settings


@pytest.fixture()
def client(composer, catalog, verdicts, tmp_path):
    engine = Engine(Settings(runs=tmp_path, llm_backend="none"), catalog, verdicts, composer)
    with TestClient(create_app(engine)) as c:
        yield c


def test_health(client):
    body = client.get("/api/health").json()
    assert body["status"] == "ok" and body["procedures"] == 836 and body["llm"] is False


def test_ask_returns_official_card(client):
    body = client.post("/api/ask", json={"question": "Combien coûte le timbre pour des renseignements sur un titre foncier ?"}).json()
    assert body["status"] == "held" and body["procedure_key"] == "fr183"


def test_ask_validates_input(client):
    assert client.post("/api/ask", json={"question": ""}).status_code == 422


def test_quality_lists_only_confirmed(client):
    body = client.get("/api/quality").json()
    assert body["confirmed"] == 63 and body["misfiled"] == 3 and all(c["status"] == "confirmed" for c in body["conflicts"])


def test_exercise_verify_and_decide(client):
    run = client.post("/api/exercise", json={"stages": ["S6"]}).json()
    assert run["chain_ok"]
    assert client.get(f"/api/runs/{run['run']}/verify").json()["chain_ok"]
    bad = client.post(f"/api/runs/{run['run']}/decisions", json={"seq": 0, "action": "x", "decision": "approve", "by": "Officer"})
    assert bad.status_code == 400


def test_run_ids_are_validated(client):
    assert client.get("/api/runs/..%2F..%2Fetc/verify").status_code == 404
    assert client.get("/api/runs/not-a-run/verify").status_code == 404


def test_plain_needs_a_model(client):
    body = client.post("/api/ask", json={"question": "Combien coûte le renouvellement de permis de conduire ?", "plain": True}).json()
    assert body["plain"]["accepted"] is False and body["plain"]["reason"] == "no LLM configured"


def test_asks_are_ledgered(client):
    body = client.post("/api/ask", json={"question": "Mon NNI est 1234567890"}).json()
    assert "ledger_seq" in body and "1234567890" not in body["query"]


def test_web_page_served(client):
    r = client.get("/")
    assert r.status_code == 200 and "LexCivis" in r.text


def test_stale_service_worker_is_removed(client):
    r = client.get("/sw.js")
    assert r.status_code == 200 and "unregister" in r.text and r.headers["content-type"].startswith("text/javascript")
    assert client.get("/").headers["cache-control"] == "no-cache"


def test_source_entry_is_the_raw_record(client):
    body = client.get("/api/sources/66/fr").json()
    assert body["file"] == "data/procedures.json" and body["entry"] == 66
    assert "url" not in body["record"] and "Frais afférents à la procédure" in body["record"]["fields"]
    assert client.get("/api/sources/0/fr").status_code == 404


def test_answer_cites_file_entry_and_field(client):
    body = client.post("/api/ask", json={"question": "Combien coûte le timbre pour des renseignements sur un titre foncier ?"}).json()
    item = body["items"][0]
    assert item["source"]["file"] == "data/procedures.json" and item["source"]["field"]
    assert "url" not in body and all("url" not in i and "http" not in str(i["source"]) for i in body["items"])


def test_documents_are_served_by_page(client):
    lib = client.get("/api/library").json()
    if not lib["documents"]:
        return
    doc = lib["list"][0]
    assert client.get(f"/api/documents/{doc['id']}/pages/1").json()["page"] == 1
    image = client.get(f"/api/documents/{doc['id']}/pages/1/image")
    assert image.status_code == 200 and image.headers["content-type"] == "image/png"
    assert client.get("/api/documents/../../etc/passwd").status_code == 404

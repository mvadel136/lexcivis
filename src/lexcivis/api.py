import hmac
import json
import os
import re
import threading
import time
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from dataclasses import asdict
from pathlib import Path

from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field as PydField

from . import __version__
from .catalog import SOURCE_FILE, Field
from .documents import Library
from .engine import Engine, load_engine
from .governance.exercise import RUN_ID, load_config, record_decision, run_exercise
from .governance.ledger import Ledger, verify
from .governance.seal import check
from .llm import chat_model, plain_language
from .profile import profile
from .quality import audit
from .settings import ROOT

WEB = ROOT / "web"
RESET_WORKER = """self.addEventListener("install", () => self.skipWaiting());
self.addEventListener("activate", (event) => {
  event.waitUntil((async () => {
    for (const key of await caches.keys()) await caches.delete(key);
    await self.registration.unregister();
    for (const client of await self.clients.matchAll({ type: "window" })) client.navigate(client.url);
  })());
});
"""
LIMITS = {"ask": (30, 60), "exercise": (4, 60), "approve": (20, 60)}


class AskRequest(BaseModel):
    question: str = PydField(min_length=1, max_length=1000)
    lang: str | None = PydField(default=None, pattern="^(fr|ar)$")
    plain: bool = False


class ExerciseRequest(BaseModel):
    stages: list[str] = PydField(default_factory=list, max_length=7)
    inject: str = PydField(default="", max_length=600)
    inject_question: str = PydField(default="", max_length=600)
    use_llm: bool = False


class DecisionRequest(BaseModel):
    seq: int = PydField(ge=0)
    action: str = PydField(min_length=1, max_length=80)
    decision: str = PydField(pattern="^(approve|reject)$")
    by: str = PydField(min_length=2, max_length=80)
    note: str = PydField(default="", max_length=400)


class RateLimiter:
    def __init__(self):
        self.hits: dict[tuple[str, str], deque] = defaultdict(deque)
        self.lock = threading.Lock()

    def check(self, bucket: str, client: str) -> None:
        limit, window = LIMITS[bucket]
        now = time.monotonic()
        with self.lock:
            q = self.hits[(bucket, client)]
            while q and now - q[0] > window:
                q.popleft()
            if len(q) >= limit:
                raise HTTPException(429, "too many requests, try again in a minute")
            q.append(now)


def create_app(engine: Engine | None = None) -> FastAPI:
    state: dict = {}
    limiter = RateLimiter()
    model_lock = threading.Semaphore(int(os.environ.get("LEXCIVIS_WORKERS", "2")))
    token = os.environ.get("LEXCIVIS_TOKEN", "")

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        e = engine or await run_in_threadpool(load_engine)
        state["engine"] = e
        state["model"] = chat_model(e.settings)
        state["quality"] = audit(e.catalog, e.verdicts)
        state["profile"] = profile(e.catalog, e.verdicts)[0]
        state["library"] = Library(e.settings.library_path, e.settings.runs / "page-cache")
        state["rows"] = json.loads(e.settings.data_path.read_text(encoding="utf-8"))
        state["asks"] = Ledger(e.settings.runs / "ask" / "ledger.jsonl")
        if state["asks"].path.exists() and state["asks"].path.stat().st_size:
            state["asks"] = Ledger.resume(state["asks"].path)
        state["asks_lock"] = threading.Lock()
        state["asks"].append("server_start", "ORCHESTRATOR", e.provenance)
        trusted = e.settings.trusted_key
        state["trusted"] = trusted.read_text(encoding="utf-8") if trusted.exists() else None
        state["signing"] = (e.settings.signing_key, e.settings.signer)
        yield

    app = FastAPI(title="LexCivis", version=__version__, lifespan=lifespan)

    def client_of(request: Request) -> str:
        return request.client.host if request.client else "unknown"

    def privileged(request: Request, x_lexcivis_token: str = Header(default="")) -> bool:
        if token:
            return hmac.compare_digest(x_lexcivis_token, token)
        return client_of(request) in ("127.0.0.1", "::1", "testclient")

    def answer(question: str, lang: str | None):
        with model_lock:
            return state["engine"].composer.answer(question, lang)

    def documents_for(a) -> list[dict]:
        library, out, seen = state["library"], [], set()
        p = state["engine"].catalog.get(a.procedure_key) if a.procedure_key else None
        if not p:
            return out
        basis = " ".join(r.get(Field.LEGAL_BASIS) for r in p.records)
        query = " ".join([a.query, a.title, basis])
        found = [(library.resolve(x["file"]), "attached") for x in a.attachments]
        found += [(d, "cited") for d in library.cited(basis)]
        for d, relation in found:
            if not d or d["id"] in seen:
                continue
            seen.add(d["id"])
            out.append({"id": d["id"], "label": d["labels"][0] if d["labels"] else d["names"][0].split("/")[-1],
                        "name": d["names"][0], "kind": d["kind"], "type": d["type"], "pages": d["pages"],
                        "ocr_pages": d["ocr_pages"], "relation": relation, "best": library.best_page(d["id"], query)})
        return out

    def document(doc_id: str) -> dict:
        d = state["library"].documents.get(doc_id)
        if not d:
            raise HTTPException(404, "unknown document")
        return d

    def run_dir(run_id: str) -> Path:
        if not re.fullmatch(RUN_ID, run_id):
            raise HTTPException(404, "unknown run")
        path = state["engine"].settings.runs / run_id / "ledger.jsonl"
        if not path.exists():
            raise HTTPException(404, "unknown run")
        return path

    @app.get("/api/health")
    def health() -> dict:
        e = state["engine"]
        return {"status": "ok", "version": __version__, "procedures": len(e.catalog), "llm": bool(state["model"]),
                "provenance": e.provenance}

    @app.post("/api/ask")
    async def ask(req: AskRequest, request: Request, can_llm: bool = Depends(privileged)) -> dict:
        limiter.check("ask", client_of(request))
        a = await run_in_threadpool(answer, req.question, req.lang)
        out = a.to_dict()
        out["documents"] = documents_for(a)
        out["plain"] = {"text": "", "accepted": False, "reason": ""}
        if req.plain and a.status == "answered":
            if not state["model"]:
                out["plain"]["reason"] = "no LLM configured"
            elif not can_llm:
                out["plain"]["reason"] = "LLM rephrasing needs the access token"
            else:
                out["plain"] = asdict(await run_in_threadpool(plain_language, state["model"], a))
        with state["asks_lock"]:
            seq = state["asks"].append("ask", "CITIZEN", {"query": a.query, "status": a.status, "procedure": a.procedure_key,
                                                          "intent": a.intent, "masked": a.masked, "claims": a.claims,
                                                          "values": [i.value or f"FR: {i.fr_value} | AR: {i.ar_value}" for i in a.items],
                                                          "plain": out["plain"]["reason"]})["seq"]
        out["ledger_seq"] = seq
        return out

    @app.get("/api/procedures/{key}")
    def procedure(key: str) -> dict:
        p = state["engine"].catalog.get(key)
        if not p:
            raise HTTPException(404, "unknown procedure")
        return {"key": p.key, "records": [{**asdict(r), "fields": {f.value: v for f, v in r.fields.items()}} for r in p.records]}

    @app.get("/api/sources/{entry}/{lang}")
    def source(entry: int, lang: str) -> dict:
        rows = state["rows"]
        if lang not in ("fr", "ar") or not 1 <= entry <= len(rows) or not rows[entry - 1].get(lang):
            raise HTTPException(404, "unknown source entry")
        rec = rows[entry - 1][lang]
        library = state["library"]
        attachments = [{**x, "document": (library.resolve(x["file"]) or {}).get("id", "")} for x in rec.get("attachments") or []]
        return {"file": SOURCE_FILE, "entry": entry, "lang": lang,
                "record": {**rec, "attachments": attachments}}

    @app.get("/api/documents/{doc_id}")
    def document_meta(doc_id: str) -> dict:
        d = document(doc_id)
        pages = state["library"].pages(doc_id)
        return {**d, "methods": [p["method"] for p in pages]}

    @app.get("/api/documents/{doc_id}/pages/{page}")
    def document_page(doc_id: str, page: int) -> dict:
        document(doc_id)
        pages = state["library"].pages(doc_id)
        if not 1 <= page <= len(pages):
            raise HTTPException(404, "unknown page")
        p = pages[page - 1]
        return {"page": page, "pages": len(pages), "method": p["method"], "text": p["text"]}

    @app.get("/api/documents/{doc_id}/pages/{page}/image")
    def document_image(doc_id: str, page: int) -> FileResponse:
        document(doc_id)
        png = state["library"].page_png(doc_id, page)
        if png is None:
            raise HTTPException(404, "unknown page")
        return FileResponse(png, media_type="image/png", headers={"Cache-Control": "max-age=86400"})

    @app.get("/api/documents/{doc_id}/original")
    def document_original(doc_id: str) -> FileResponse:
        d = document(doc_id)
        path = state["library"].original(doc_id)
        if path is None:
            raise HTTPException(404, "file not available")
        return FileResponse(path, filename=d["names"][0].split("/")[-1])

    @app.get("/api/library")
    def library_summary() -> dict:
        lib = state["library"]
        docs = list(lib.documents.values())
        return {"documents": len(docs), "attachments": len(lib.names) + len(lib.broken),
                "legal_texts": sum(1 for d in docs if d["kind"] == "legal_text"),
                "forms": sum(1 for d in docs if d["kind"] == "form"),
                "pages": sum(d["pages"] for d in docs), "ocr_pages": sum(d["ocr_pages"] for d in docs),
                "duplicates": len(lib.names) - len(docs), "broken": lib.broken,
                "list": [{k: d[k] for k in ("id", "labels", "names", "kind", "type", "pages", "ocr_pages", "procedures", "sha256")}
                         for d in sorted(docs, key=lambda d: -len(d["procedures"]))]}

    @app.get("/api/quality")
    def quality() -> dict:
        report = state["quality"].to_dict()
        report["conflicts"] = [c for c in report["conflicts"] if c["status"] == "confirmed"]
        catalog = state["engine"].catalog
        keys = {c["key"] for c in report["conflicts"]} | {k for g in report["duplicate_titles"] for k in g}
        report["titles"] = {k: catalog.get(k).title("fr") for k in keys if catalog.get(k)}
        return report

    @app.get("/api/profile")
    def data_profile() -> dict:
        return state["profile"]

    @app.get("/api/governance")
    def governance() -> dict:
        cfg = load_config()
        return {key: cfg[key] for key in ("agents", "coordination", "stages", "gaps", "dimensions")}

    @app.post("/api/exercise")
    async def exercise(req: ExerciseRequest, request: Request, can_llm: bool = Depends(privileged)) -> dict:
        limiter.check("exercise", client_of(request))
        if req.use_llm and not can_llm:
            raise HTTPException(403, "LLM agents need the access token")
        e = state["engine"]
        model = state["model"] if req.use_llm else None

        def go():
            with model_lock:
                return run_exercise(e.composer, e.settings.runs, model, req.stages or None, req.inject,
                                    req.inject_question, e.provenance, state["signing"])

        run = await run_in_threadpool(go)
        stages = [{"stage": {k: r.stage.get(k) for k in ("id", "day", "title", "simulated")},
                   "answers": [{k: a[k] for k in ("query", "status", "title", "source", "hassaniya", "masked", "items", "notes")}
                               for a in r.answers],
                   "board": r.board} for r in run.results]
        sealed, detail = check(run.directory / "ledger.jsonl", state["trusted"])
        return {"run": run.directory.name, "chain_ok": run.chain_ok, "records": run.records, "stages": stages,
                "sealed": sealed, "seal": detail,
                "brief": (run.directory / "case_brief.md").read_text(encoding="utf-8")}

    @app.get("/api/runs/{run_id}/verify")
    def verify_run(run_id: str) -> dict:
        path = run_dir(run_id)
        ok, n, bad = verify(path)
        sealed, detail = check(path, state["trusted"])
        return {"chain_ok": ok, "records": n, "first_bad_seq": bad, "sealed": sealed, "seal": detail}

    @app.post("/api/runs/{run_id}/decisions")
    def decide(run_id: str, req: DecisionRequest, request: Request, allowed: bool = Depends(privileged)) -> dict:
        limiter.check("approve", client_of(request))
        if not allowed:
            raise HTTPException(403, "human decisions need the access token")
        try:
            record = record_decision(run_dir(run_id), req.seq, req.action, req.decision, req.by, req.note, state["signing"])
        except ValueError as exc:
            raise HTTPException(400, str(exc)) from exc
        return {"seq": record["seq"], "hash": record["hash"]}

    if WEB.exists():
        app.mount("/static", StaticFiles(directory=WEB), name="static")

        @app.get("/")
        def index() -> FileResponse:
            return FileResponse(WEB / "index.html", headers={"Cache-Control": "no-cache"})

        @app.get("/sw.js")
        def reset_worker() -> Response:
            return Response(RESET_WORKER, media_type="text/javascript", headers={"Cache-Control": "no-store"})

    return app

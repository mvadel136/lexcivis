import json
import re
import shutil
from pathlib import Path

from .catalog import SOURCE_FILE
from .documents import Library

PROCEDURES = "Mauritania_Procedures"
TEXTS = "Mauritania_Legal_Texts_and_Forms"
LAW = "Mauritania_Data_Protection_Law"


def _slug(text: str, size: int = 60) -> str:
    s = re.sub(r"[^\w]+", "_", text, flags=re.UNICODE).strip("_")
    return s[:size] or "untitled"


def _fields(raw) -> dict:
    return raw if isinstance(raw, dict) else {}


def _procedure(entry: int, row: dict, library: Library) -> str:
    fr, ar = row.get("fr") or {}, row.get("ar") or {}
    lines = [f"# {fr.get('title') or ar.get('title')}", ""]
    if fr and ar:
        lines += [f"Arabic title: {ar.get('title', '')}", ""]
    lines += [f"- Source: {SOURCE_FILE}, entry {entry}",
              f"- Administration: {fr.get('ministry') or ar.get('ministry', '')}",
              f"- Category: {fr.get('category') or ar.get('category', '')}"]
    for lang, rec in (("fr", fr), ("ar", ar)):
        if rec:
            lines.append(f"- {lang.upper()} record {rec.get('id')}, last update {rec.get('last_update', '')}")
    attached = []
    for rec in (fr, ar):
        for a in rec.get("attachments") or []:
            d = library.resolve(a["file"])
            if d and d["id"] not in attached:
                attached.append(d["id"])
                lines.append(f"- Attached: {a.get('label', '')} ({TEXTS}/{_document_name(d)})")
    for title, rec in (("Version française", fr), ("النسخة العربية", ar)):
        if not rec:
            continue
        lines += ["", f"## {title} (record {rec.get('id')})", ""]
        for label, value in _fields(rec.get("fields")).items():
            lines += [f"### {label}", "", str(value).strip(), ""]
    return "\n".join(lines).rstrip() + "\n"


def _document_name(d: dict) -> str:
    label = d["labels"][0] if d["labels"] else Path(d["names"][0]).stem
    return f"{d['id']}_{_slug(label)}.md"


def _document(d: dict, library: Library) -> str:
    label = d["labels"][0] if d["labels"] else Path(d["names"][0]).stem
    lines = [f"# {label}", "",
             f"- Kind: {'form' if d['kind'] == 'form' else 'legal text'}",
             f"- Original files: {'; '.join(d['names'])}",
             f"- SHA-256: {d['sha256']}",
             f"- Pages: {d['pages']} ({d['ocr_pages']} read by OCR, French and Arabic)",
             f"- Attached to {SOURCE_FILE} entries: {', '.join(str(e) for e in d['procedures'])}"]
    if len(d["labels"]) > 1:
        lines.append(f"- Other titles: {'; '.join(d['labels'][1:])}")
    for p in library.pages(d["id"]):
        lines += ["", f"## Page {p['page']}" + (" (OCR)" if p["method"] == "ocr" else ""), "", p["text"].strip()]
    return "\n".join(lines).rstrip() + "\n"


def _law(law: dict) -> str:
    lines = ["# Loi n° 2017-020 du 22 juillet 2017 relative à la protection des données à caractère personnel", "",
             f"- Source: {law.get('source', '')}", ""]
    for number, text in sorted(law["articles"].items(), key=lambda kv: int(re.match(r"\d+", kv[0])[0])):
        lines += [f"## Article {number}", "", text.strip(), ""]
    return "\n".join(lines).rstrip() + "\n"


def export_inputdocs(procedures: str | Path, library_root: str | Path, law_path: str | Path, out: str | Path) -> dict:
    out = Path(out)
    if out.exists():
        shutil.rmtree(out)
    rows = json.loads(Path(procedures).read_text(encoding="utf-8"))
    library = Library(library_root)
    law = json.loads(Path(law_path).read_text(encoding="utf-8"))
    (out / PROCEDURES).mkdir(parents=True)
    (out / TEXTS).mkdir()
    (out / LAW).mkdir()
    for entry, row in enumerate(rows, start=1):
        title = (row.get("fr") or row.get("ar") or {}).get("title", "")
        (out / PROCEDURES / f"entry_{entry:04d}_{_slug(title)}.md").write_text(_procedure(entry, row, library), encoding="utf-8")
    for d in library.documents.values():
        (out / TEXTS / _document_name(d)).write_text(_document(d, library), encoding="utf-8")
    (out / LAW / "Loi_2017-020_protection_des_donnees.md").write_text(_law(law), encoding="utf-8")
    summary = {"procedures": len(rows), "documents": len(library), "law_articles": len(law["articles"])}
    (out / "inputs.md").write_text(
        "# LexCivis knowledge base for the ITU AI Readiness toolkit\n\n"
        f"Drop this folder into `simulation/server/knowledge/` and run "
        f"`python -m server.knowledge.ingest --dir server/knowledge/InputDocs`.\n\n"
        f"- `{PROCEDURES}/`: {summary['procedures']} procedures, French and Arabic versions, one file each, "
        f"citing `{SOURCE_FILE}` and the entry number.\n"
        f"- `{TEXTS}/`: {summary['documents']} legal texts and forms attached to the procedures, page by page.\n"
        f"- `{LAW}/`: Law 2017-020, {summary['law_articles']} articles.\n", encoding="utf-8")
    return summary

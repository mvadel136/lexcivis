import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import tempfile
import threading
from collections import Counter
from pathlib import Path

from .text import tokens

OFFICE = (".doc", ".docx", ".odt", ".rtf")
COMMON = set("""les des une pour par sur dans avec aux est sont qui que quoi quel quelle quels quelles comment combien faut
leur leurs ses son cette ces être etre avoir fait faire tout tous toute plus moins elle elles ils nous vous
portant relatif relative fixant decret arrete loi article articles vu present conformement dispositions
the and for with from that this what which
في من على إلى الى عن مع هذا هذه التي الذي الذين ما هي هو كيف كم ماذا لماذا او أو ثم كل بعد قبل""".split())
NUMBER = re.compile(r"(?<!\d)(\d{2,4})\s*[-/–]\s*(\d{2,4})(?!\d)")
_lock = threading.Lock()


def law_numbers(text: str) -> set[str]:
    out = set()
    for a, b in NUMBER.findall(text or ""):
        if len(a) == 4 and 1950 <= int(a) <= 2030:
            out.add(f"{a}-{int(b):03d}")
        elif len(b) == 4 and 1950 <= int(b) <= 2030:
            out.add(f"{b}-{int(a):03d}")
    return out


class Library:
    def __init__(self, root: str | Path, cache: str | Path | None = None):
        self.root = Path(root)
        self.cache = Path(cache) if cache else self.root / ".cache"
        manifest = self.root / "manifest.json"
        data = json.loads(manifest.read_text(encoding="utf-8")) if manifest.exists() else {"documents": [], "names": {}, "broken": []}
        self.documents = {d["id"]: d for d in data["documents"]}
        self.names = data["names"]
        self.broken = data.get("broken", [])
        self._pages = {}
        self._by_number = {}
        for d in self.documents.values():
            for n in law_numbers(" ".join(d["labels"] + d["names"])):
                self._by_number.setdefault(n, []).append(d["id"])

    def __len__(self) -> int:
        return len(self.documents)

    def resolve(self, name: str) -> dict | None:
        doc_id = self.names.get(name)
        return self.documents.get(doc_id) if doc_id else None

    def cited(self, text: str) -> list[dict]:
        seen, out = set(), []
        for n in sorted(law_numbers(text)):
            for doc_id in self._by_number.get(n, []):
                if doc_id not in seen:
                    seen.add(doc_id)
                    out.append(self.documents[doc_id])
        return out

    def pdf(self, doc_id: str) -> Path | None:
        d = self.documents.get(doc_id)
        if not d:
            return None
        p = self.root / d["pdf"]
        return p if p.exists() else None

    def original(self, doc_id: str) -> Path | None:
        d = self.documents.get(doc_id)
        if not d:
            return None
        p = self.root / d["file"]
        return p if p.exists() else None

    def pages(self, doc_id: str) -> list[dict]:
        if doc_id not in self._pages:
            p = self.root / "pages" / f"{doc_id}.json"
            self._pages[doc_id] = json.loads(p.read_text(encoding="utf-8")) if p.exists() else []
        return self._pages[doc_id]

    def page_png(self, doc_id: str, page: int) -> Path | None:
        import fitz

        pdf = self.pdf(doc_id)
        if pdf is None:
            return None
        target = self.cache / doc_id / f"{page}.png"
        with _lock:
            if not target.exists():
                with fitz.open(pdf) as doc:
                    if not 1 <= page <= doc.page_count:
                        return None
                    target.parent.mkdir(parents=True, exist_ok=True)
                    doc[page - 1].get_pixmap(matrix=fitz.Matrix(1.5, 1.5)).save(target)
        return target

    def best_page(self, doc_id: str, query: str) -> dict:
        pages = self.pages(doc_id)
        terms = [t for t in tokens(query) if len(t) > 2 and t not in COMMON]
        if not pages or not terms:
            return {"page": 1, "score": 0.0, "matched": []}
        df = Counter()
        bags = []
        for p in pages:
            bag = Counter(tokens(p["text"]))
            bags.append(bag)
            df.update(set(bag))
        n = len(pages)
        best = (0.0, 1, [])
        for i, bag in enumerate(bags, start=1):
            hit = [t for t in set(terms) if bag[t]]
            score = sum((1 + math.log(bag[t])) * math.log(1 + n / df[t]) for t in hit)
            if score > best[0]:
                best = (score, i, hit)
        return {"page": best[1], "score": round(best[0], 3), "matched": sorted(best[2])}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _to_pdf(src: Path, out_dir: Path) -> Path | None:
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(["soffice", "--headless", f"-env:UserInstallation=file://{tmp}/profile", "--convert-to", "pdf",
                        "--outdir", tmp, str(src)], check=False, capture_output=True, timeout=180)
        made = Path(tmp) / (src.stem + ".pdf")
        if not made.exists():
            return None
        out_dir.mkdir(parents=True, exist_ok=True)
        target = out_dir / made.name
        shutil.move(made, target)
        return target


def _ocr(page, lang: str) -> str:
    import fitz

    with tempfile.TemporaryDirectory() as tmp:
        img = Path(tmp) / "p.png"
        page.get_pixmap(matrix=fitz.Matrix(300 / 72, 300 / 72), colorspace=fitz.csGRAY).save(img)
        r = subprocess.run(["tesseract", str(img), "stdout", "-l", lang, "--psm", "3"], capture_output=True, text=True,
                           timeout=300, env={**os.environ, "OMP_THREAD_LIMIT": "1"})
        return r.stdout.strip()


def _script(text: str) -> str:
    arabic = sum(1 for c in text if "؀" <= c <= "ۿ")
    latin = sum(1 for c in text if c.isascii() and c.isalpha())
    return "ara" if arabic > latin else "fra"


def build_library(procedures: str | Path, source: str | Path, out: str | Path, ocr_lang: str = "fra+ara") -> dict:
    import fitz

    source, out = Path(source), Path(out)
    rows = json.loads(Path(procedures).read_text(encoding="utf-8"))
    refs = {}
    for entry, row in enumerate(rows, start=1):
        for lang in ("fr", "ar"):
            rec = row.get(lang) or {}
            for a in rec.get("attachments") or []:
                r = refs.setdefault(a["file"], {"labels": set(), "procedures": set(), "type": a.get("type", "")})
                if a.get("label"):
                    r["labels"].add(a["label"].strip())
                r["procedures"].add(entry)
    documents, names, broken = {}, {}, []
    for name in sorted(refs):
        path = source / name
        if not path.is_file():
            broken.append({"name": name, "reason": "missing"})
            continue
        if path.name.startswith("._"):
            broken.append({"name": name, "reason": "macos_metadata_not_a_document"})
            continue
        doc_id = _sha(path)[:16]
        names[name] = doc_id
        d = documents.get(doc_id)
        if d is None:
            ext = path.suffix.lower()
            stored = out / "files" / f"{doc_id}{ext}"
            stored.parent.mkdir(parents=True, exist_ok=True)
            if not stored.exists():
                shutil.copy2(path, stored)
            pdf = stored if ext == ".pdf" else None
            if ext in OFFICE:
                rendered = out / "rendered" / f"{doc_id}.pdf"
                if not rendered.exists():
                    made = _to_pdf(stored, out / "rendered")
                    if made:
                        made.rename(rendered)
                pdf = rendered if rendered.exists() else None
            d = documents[doc_id] = {
                "id": doc_id, "sha256": _sha(stored), "file": str(stored.relative_to(out)),
                "pdf": str(pdf.relative_to(out)) if pdf else "", "type": ext.lstrip("."), "kind": "",
                "names": [], "labels": set(), "procedures": set(), "pages": 0, "ocr_pages": 0, "script": "",
            }
        d["names"].append(name)
        d["labels"] |= refs[name]["labels"]
        d["procedures"] |= refs[name]["procedures"]
        d["kind"] = "form" if name.startswith("formulaires/") else "legal_text"
    for doc_id, d in documents.items():
        page_file = out / "pages" / f"{doc_id}.json"
        if page_file.exists():
            pages = json.loads(page_file.read_text(encoding="utf-8"))
        else:
            pages = []
            if d["pdf"]:
                try:
                    with fitz.open(out / d["pdf"]) as doc:
                        for i, page in enumerate(doc, start=1):
                            text = page.get_text().strip()
                            method = "text_layer"
                            if len(text) < 40:
                                text, method = _ocr(page, ocr_lang), "ocr"
                            pages.append({"page": i, "method": method, "text": text})
                except (RuntimeError, ValueError):
                    d["pdf"] = ""
            page_file.parent.mkdir(parents=True, exist_ok=True)
            page_file.write_text(json.dumps(pages, ensure_ascii=False, indent=0), encoding="utf-8")
        d["pages"] = len(pages)
        d["ocr_pages"] = sum(1 for p in pages if p["method"] == "ocr")
        d["script"] = _script(" ".join(p["text"] for p in pages[:3]))
    docs = []
    for d in documents.values():
        d["labels"] = sorted(d["labels"])
        d["procedures"] = sorted(d["procedures"])
        d["names"] = sorted(d["names"])
        docs.append(d)
    manifest = {"source_rows": len(rows), "attachments": len(refs), "documents": sorted(docs, key=lambda d: d["id"]),
                "names": names, "broken": broken}
    (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
    return {"attachments": len(refs), "documents": len(docs), "broken": len(broken),
            "pages": sum(d["pages"] for d in docs), "ocr_pages": sum(d["ocr_pages"] for d in docs),
            "unreadable": sum(1 for d in docs if not d["pages"])}

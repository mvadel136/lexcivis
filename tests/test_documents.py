import json
from pathlib import Path

import pytest

from lexcivis.documents import Library, law_numbers

ROOT = Path(__file__).resolve().parents[1]
LIBRARY = ROOT / "data" / "documents"


@pytest.fixture(scope="module")
def library():
    if not (LIBRARY / "manifest.json").exists():
        pytest.skip("document library not built")
    return Library(LIBRARY, LIBRARY / ".cache")


def test_law_numbers_cover_both_orders():
    assert law_numbers("Décret n° 2019-056 et loi 2017/020") == {"2019-056", "2017-020"}
    assert law_numbers("Arrêté 1487/2021") == {"2021-1487"}
    assert law_numbers("page 12-14") == set()


def test_every_attachment_resolves_or_is_reported(library):
    rows = json.loads((ROOT / "data" / "procedures.json").read_text(encoding="utf-8"))
    names = {a["file"] for r in rows for lang in ("fr", "ar") for a in (r.get(lang) or {}).get("attachments") or []}
    broken = {b["name"] for b in library.broken}
    assert names == set(library.names) | broken
    assert all(library.documents[i]["pages"] > 0 for i in set(library.names.values()))


def test_stored_files_match_their_hash(library):
    import hashlib

    for d in list(library.documents.values())[:10]:
        assert hashlib.sha256((LIBRARY / d["file"]).read_bytes()).hexdigest() == d["sha256"]


def test_best_page_finds_the_article(library):
    doc = library.resolve(next(n for n in library.names if "2000-05" in n and n.endswith(".pdf")))
    best = library.best_page(doc["id"], "agences et bureaux de voyages licence")
    assert 1 <= best["page"] <= doc["pages"] and "voyages" in best["matched"]


def test_cited_legal_basis_is_found_by_number(library):
    assert any("2000-05" in " ".join(d["names"]) for d in library.cited("Décret 2000/05 du 16/02/2000"))


def test_inputdocs_export_matches_the_toolkit_layout(library, tmp_path):
    from lexcivis.inputdocs import export_inputdocs

    law = ROOT / "src" / "lexcivis" / "governance" / "resources" / "law_2017_020.json"
    summary = export_inputdocs(ROOT / "data" / "procedures.json", LIBRARY, law, tmp_path / "InputDocs")
    files = list((tmp_path / "InputDocs").rglob("*.md"))
    assert summary == {"procedures": 836, "documents": len(library), "law_articles": 101}
    assert len(files) == 836 + len(library) + 2
    assert all(f.parent.parent.name == "InputDocs" or f.name == "inputs.md" for f in files)
    assert "data/procedures.json, entry 66" in next((tmp_path / "InputDocs").rglob("entry_0066_*.md")).read_text(encoding="utf-8")

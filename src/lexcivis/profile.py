import json
import re
import statistics
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path

from .catalog import Catalog, Field, Procedure, Record
from .quality import Verdicts, conflicts, duplicate_titles
from .text import normalize

KEY_FIELDS = (Field.DOCUMENTS, Field.FEE, Field.DELAY, Field.RECEPTION, Field.LEGAL_BASIS, Field.CONTACT)
_PLACEHOLDER = re.compile(r"^(non specifi\w*|non precise\w*|non defini\w*|non concerne\w*(?: \(n/a\))?|indetermine\w*|variable\w*|relatif|non|-|nan|n/a|"
                          r"غير محدد\w*|غير معروف\w*|متغير\w*|نسبي)\.?$")
_NOT_DURATION = re.compile(r"a la demande|au jour le jour|illimite|non defini|selon|variable|relatif|mensuel|annuel|depend|"
                           r"حسب|غير محدد|متغير|نسبي|حسب الطلب")
_FREE = re.compile(r"\b(gratuit\w*|neant|aucun\w*|acune|sans frais|sans taxe\w*|0 mru|0 um|service gratuit)\b|مجان|لا شيء|العدم|بدون رسوم|دون مقابل|0 اوقيه")
_VAGUE = re.compile(r"\b(selon|en fonction|variable|voir|depend|suivant|relatif|fixe par|devis|deliberation|prix des)\w*|حسب|وفق|يختلف|متغير")
_AMOUNT = re.compile(r"(\d[\d\s.,]*)\s*\(?\s*(mru|um|ouguiya\w*|ouguiyas|اوقيه|او-ج|اوج|ا\.ج)", re.I)
_PERCENT = re.compile(r"\d+(?:[.,]\d+)?\s*%|٪")
_DURATION = re.compile(r"(\d+(?:[.,]\d+)?)\s*(?:\(?\s*\d*\s*\)?\s*)?(minute|min|heure|h\b|jour|j\b|semaine|mois|an\b|annee|"
                       r"دقيق|ساع|يوم|ايام|اسبوع|اسابيع|شهر|اشهر|سن)", re.I)
_UNIT_DAYS = {"minute": 1 / 1440, "min": 1 / 1440, "heure": 1 / 24, "h": 1 / 24, "jour": 1, "j": 1, "semaine": 7, "mois": 30,
              "an": 365, "annee": 365, "دقيق": 1 / 1440, "ساع": 1 / 24, "يوم": 1, "ايام": 1, "اسبوع": 7, "اسابيع": 7,
              "شهر": 30, "اشهر": 30, "سن": 365}
_WORD_DURATIONS = {"immediat": 0, "le meme jour": 0, "meme jour": 0, "fora": 0, "فورا": 0, "فوري": 0, "في نفس اليوم": 0,
                   "une semaine": 7, "un mois": 30, "un jour": 1, "يوم واحد": 1, "اسبوع واحد": 7, "شهر واحد": 30,
                   "deux semaines": 14, "اسبوعان": 14, "يومان": 2, "une annee": 365, "un an": 365}


def is_placeholder(value: str) -> bool:
    return bool(_PLACEHOLDER.match(normalize(value).strip(" .")))


def fee_kind(value: str) -> tuple[str, list[float], bool]:
    v = normalize(value)
    if not v:
        return "missing", [], False
    if is_placeholder(value) and not _FREE.search(v):
        return "unspecified", [], False
    amounts, old = [], False
    for number, unit in _AMOUNT.findall(v):
        digits = re.sub(r"[\s.,](?=\d{3}\b)", "", number.strip()).replace(",", ".").rstrip(".")
        try:
            amount = float(digits)
        except ValueError:
            continue
        if unit.lower() == "um":
            old = True
            amount /= 10
        amounts.append(amount)
    if amounts:
        return "amount", amounts, old
    if _PERCENT.search(v):
        return "percentage", [], False
    if _FREE.search(v):
        return "free", [0.0], False
    if _VAGUE.search(v):
        return "depends", [], False
    return "other", [], False


def delay_kind(value: str) -> str:
    v = normalize(value)
    if not v:
        return "missing"
    if delay_days(value):
        return "duration"
    if is_placeholder(value) or _NOT_DURATION.search(v):
        return "not a duration"
    return "other"


def delay_days(value: str) -> tuple[float, float] | None:
    v = normalize(value)
    if not v or is_placeholder(value):
        return None
    found = [float(n.replace(",", ".")) * _UNIT_DAYS[next(k for k in _UNIT_DAYS if u.lower().startswith(k))]
             for n, u in _DURATION.findall(v)]
    found += [days for phrase, days in _WORD_DURATIONS.items() if phrase in v]
    return (min(found), max(found)) if found else None


def documents_count(value: str) -> int:
    parts = [p for p in re.split(r"\n|;|؛|•|(?:^|\s)-\s|\d+[.)]\s", value) if len(p.strip()) > 3]
    return len(parts)


@dataclass
class NormalizedProcedure:
    key: str
    fr_id: str
    ar_id: str
    title_fr: str
    title_ar: str
    ministry: str
    category: str
    last_update: str
    languages: str
    fee_kind: str
    fee_amounts_mru: list
    fee_old_currency: bool
    delay_kind: str
    delay_min_days: float | None
    delay_max_days: float | None
    documents: int
    documents_ar: int
    has_legal_basis: bool
    has_specific_contact: bool
    completeness: float
    fr_ar_conflicts: list
    entry: int
    attachments: int


def _primary(p: Procedure) -> Record:
    return p.fr or p.ar


def _present(r: Record, f: Field) -> bool:
    v = r.get(f)
    return bool(v) and not is_placeholder(v)


def normalize_procedure(p: Procedure, verdicts: Verdicts, generic_contacts: set[str]) -> NormalizedProcedure:
    r = _primary(p)
    kind, amounts, old = fee_kind(r.get(Field.FEE))
    days = delay_days(r.get(Field.DELAY))
    contact = r.get(Field.CONTACT).strip().lower()
    return NormalizedProcedure(
        key=p.key, fr_id=p.fr.id if p.fr else "", ar_id=p.ar.id if p.ar else "",
        title_fr=p.fr.title if p.fr else "", title_ar=p.ar.title if p.ar else "",
        ministry=r.ministry, category=r.category, last_update=r.updated_on.isoformat() if r.updated_on else "",
        languages="fr+ar" if p.fr and p.ar else ("fr" if p.fr else "ar"),
        fee_kind=kind, fee_amounts_mru=amounts, fee_old_currency=old,
        delay_kind=delay_kind(r.get(Field.DELAY)),
        delay_min_days=days[0] if days else None, delay_max_days=days[1] if days else None,
        documents=documents_count(r.get(Field.DOCUMENTS)),
        documents_ar=documents_count(p.ar.get(Field.DOCUMENTS)) if p.ar else 0,
        has_legal_basis=any(_present(x, Field.LEGAL_BASIS) for x in p.records),
        has_specific_contact=bool(contact) and contact not in generic_contacts,
        completeness=round(sum(_present(r, f) for f in KEY_FIELDS) / len(KEY_FIELDS), 3),
        fr_ar_conflicts=[f"{c.field}:{c.status}" for c in conflicts(p, verdicts) if c.status != "false_alarm"],
        entry=r.entry, attachments=len(p.attachments),
    )


def _generic_contacts(catalog: Catalog, threshold: int = 15) -> set[str]:
    counts = Counter(r.get(Field.CONTACT).strip().lower() for p in catalog for r in p.records if r.get(Field.CONTACT))
    return {c for c, n in counts.items() if n >= threshold}


def _bucket(days: float) -> str:
    for limit, label in ((0, "same day"), (2, "≤ 2 days"), (7, "≤ 1 week"), (31, "≤ 1 month"), (92, "≤ 3 months")):
        if days <= limit:
            return label
    return "> 3 months"


def profile(catalog: Catalog, verdicts: Verdicts) -> tuple[dict, list[NormalizedProcedure]]:
    generic = _generic_contacts(catalog)
    rows = [normalize_procedure(p, verdicts, generic) for p in catalog]
    completeness = {}
    for lang in ("fr", "ar"):
        recs = [r for p in catalog for r in p.records if r.lang == lang]
        completeness[lang] = {f.value: {"filled": sum(1 for r in recs if r.get(f)),
                                        "placeholder": sum(1 for r in recs if r.get(f) and is_placeholder(r.get(f))),
                                        "records": len(recs)} for f in Field}
    by_ministry = defaultdict(list)
    for row in rows:
        by_ministry[row.ministry].append(row)
    ministries = sorted(({"ministry": m, "procedures": len(v), "completeness": round(statistics.mean(x.completeness for x in v), 3),
                          "with_legal_basis": sum(x.has_legal_basis for x in v), "with_conflict": sum(bool(x.fr_ar_conflicts) for x in v)}
                         for m, v in by_ministry.items()), key=lambda x: -x["procedures"])
    ids = {r.id for p in catalog for r in p.records}
    links = [(r.lang, rid) for p in catalog for r in p.records for rid in r.related if rid]
    amounts = [a for row in rows for a in row.fee_amounts_mru if a > 0]
    delays = [row.delay_max_days for row in rows if row.delay_max_days is not None]
    report = {
        "procedures": len(rows),
        "languages": dict(Counter(row.languages for row in rows)),
        "field_completeness": completeness,
        "fee_kinds": dict(Counter(row.fee_kind for row in rows).most_common()),
        "fee_old_currency_mentions": sum(row.fee_old_currency for row in rows),
        "fee_amount_mru": {"n": len(amounts), "median": statistics.median(amounts) if amounts else None,
                           "max": max(amounts) if amounts else None},
        "delay_buckets": dict(Counter(_bucket(d) for d in delays)),
        "delay_kinds": dict(Counter(row.delay_kind for row in rows).most_common()),
        "documents_per_procedure": {"median": statistics.median(row.documents for row in rows),
                                    "mean": round(statistics.mean(row.documents for row in rows), 2),
                                    "none": sum(1 for row in rows if row.documents == 0),
                                    "fr_ar_count_differs": sum(1 for row in rows if row.languages == "fr+ar" and row.documents and
                                                               row.documents_ar and row.documents != row.documents_ar)},
        "with_legal_basis": sum(row.has_legal_basis for row in rows),
        "generic_contact_only": sum(1 for row in rows if not row.has_specific_contact),
        "generic_contacts": sorted(generic),
        "related_links": {"total": len(links), "broken": sum(1 for _, rid in links if rid not in ids)},
        "duplicate_titles": duplicate_titles(catalog),
        "ministries": len(by_ministry),
        "least_complete_ministries": sorted((m for m in ministries if m["procedures"] >= 5), key=lambda m: m["completeness"])[:8],
        "most_complete_ministries": sorted((m for m in ministries if m["procedures"] >= 5), key=lambda m: -m["completeness"])[:8],
        "update_years": dict(sorted(Counter(row.last_update[:4] or "none" for row in rows).items())),
        "completeness_mean": round(statistics.mean(row.completeness for row in rows), 3),
    }
    return report, rows


def write_profile(catalog: Catalog, verdicts: Verdicts, out_dir: str | Path) -> dict:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    report, rows = profile(catalog, verdicts)
    (out / "data_profile.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    with (out / "procedures_normalized.jsonl").open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(asdict(row), ensure_ascii=False) + "\n")
    return report

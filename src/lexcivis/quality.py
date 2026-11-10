import json
import re
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path

from .catalog import Catalog, Field, Procedure
from .text import normalize, numbers

COMPARED = (Field.FEE, Field.DELAY)
_ZERO = re.compile(r"\b(gratuit|gratuite|neant|aucun|aucune|sans frais|sans taxe|service gratuit)\b|مجان|لا شيء|العدم|بدون رسوم|دون مقابل")


def amounts(text: str) -> list[str]:
    found = numbers(text)
    if found:
        return found
    return ["0"] if _ZERO.search(normalize(text)) else []


@dataclass(frozen=True)
class Conflict:
    key: str
    field: str
    fr: str
    ar: str
    fr_ref: dict
    ar_ref: dict
    status: str = "flagged"
    note: str = ""


class Verdicts:
    def __init__(self, entries: dict[tuple[str, str], dict] | None = None):
        self.entries = entries or {}

    @classmethod
    def load(cls, path: str | Path | None) -> "Verdicts":
        if not path or not Path(path).exists():
            return cls()
        rows = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls({(r["key"], r["field"]): r for r in rows})

    def status(self, key: str, f: Field) -> tuple[str, str]:
        v = self.entries.get((key, f.value))
        return (v["status"], v.get("note", "")) if v else ("flagged", "")


def field_conflict(p: Procedure, f: Field, verdicts: Verdicts) -> Conflict | None:
    if f not in COMPARED or not (p.fr and p.ar):
        return None
    a, b = p.fr.get(f), p.ar.get(f)
    if not (a and b):
        return None
    na, nb = amounts(a), amounts(b)
    if not (na and nb) or na == nb:
        return None
    status, note = verdicts.status(p.key, f)
    return Conflict(p.key, f.value, a, b, p.fr.ref(f), p.ar.ref(f), status, note)


def conflicts(p: Procedure, verdicts: Verdicts) -> list[Conflict]:
    return [c for f in COMPARED if (c := field_conflict(p, f, verdicts))]


@dataclass
class QualityReport:
    procedures: int
    pairs: int
    fr_only: int
    ar_only: int
    flagged: int
    confirmed: int
    false_alarms: int
    misfiled: int
    procedures_with_confirmed_conflict: int
    no_legal_basis: int
    no_fee: int
    no_delay: int
    duplicate_titles: list
    update_years: dict
    conflicts: list

    def to_dict(self) -> dict:
        d = asdict(self)
        d["conflicts"] = [asdict(c) for c in self.conflicts]
        return d


def duplicate_titles(catalog: Catalog) -> list[list[str]]:
    groups: dict[tuple[str, str], list[str]] = {}
    for p in catalog:
        r = p.record("fr")
        groups.setdefault((r.lang, normalize(r.title).strip(" .")), []).append(p.key)
    return [keys for keys in groups.values() if len(keys) > 1]


def audit(catalog: Catalog, verdicts: Verdicts) -> QualityReport:
    found = [c for p in catalog.pairs for c in conflicts(p, verdicts)]
    confirmed = [c for c in found if c.status == "confirmed"]
    years = Counter(str(r.updated_on.year) if r.updated_on else "none" for p in catalog for r in [p.record("fr")])
    return QualityReport(
        procedures=len(catalog),
        pairs=len(catalog.pairs),
        fr_only=sum(1 for p in catalog if p.fr and not p.ar),
        ar_only=sum(1 for p in catalog if p.ar and not p.fr),
        flagged=len(found),
        confirmed=len(confirmed),
        false_alarms=sum(1 for c in found if c.status == "false_alarm"),
        misfiled=sum(1 for c in found if c.status == "misfiled"),
        procedures_with_confirmed_conflict=len({c.key for c in confirmed}),
        no_legal_basis=sum(1 for p in catalog.pairs if not p.fr.get(Field.LEGAL_BASIS) and not p.ar.get(Field.LEGAL_BASIS)),
        no_fee=sum(1 for p in catalog.pairs if not p.fr.get(Field.FEE) and not p.ar.get(Field.FEE)),
        no_delay=sum(1 for p in catalog.pairs if not p.fr.get(Field.DELAY) and not p.ar.get(Field.DELAY)),
        duplicate_titles=duplicate_titles(catalog),
        update_years=dict(sorted(years.items())),
        conflicts=found,
    )

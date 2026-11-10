import json
import random
import re
from pathlib import Path

import yaml

from .catalog import Catalog, Field
from .profile import delay_kind, fee_kind, is_placeholder

_LEADING = re.compile(r"^(demande d['’]obtention d[eu']\s*|demande de |demande d['’]|demandes?\s*:?\s*|طلب الحصول على |طلب )", re.I)
_PARENS = re.compile(r"\s*\([^)]*\)\s*")


def subject(title: str) -> str:
    t = _PARENS.sub(" ", title)
    t = re.sub(r"\s*[()]\s*", " ", t).strip(" .")
    return _LEADING.sub("", t).strip() or title


def answerable(record, f: Field) -> bool:
    value = record.get(f)
    if not value or is_placeholder(value):
        return False
    if f == Field.FEE:
        return fee_kind(value)[0] in ("amount", "free")
    if f == Field.DELAY:
        return delay_kind(value) == "duration"
    return True


def generate(catalog: Catalog, templates_path: str | Path, per_cell: int = 20, seed: int = 11) -> list[dict]:
    rng = random.Random(seed)
    templates = yaml.safe_load(Path(templates_path).read_text(encoding="utf-8"))
    items = []
    for label, by_lang in templates.items():
        if label == "status":
            continue
        f = Field(label)
        for lang, patterns in by_lang.items():
            pool = [p for p in catalog.pairs if answerable(p.record(lang), f)]
            for p in rng.sample(pool, min(per_cell, len(pool))):
                pattern = rng.choice(patterns)
                items.append({"query": pattern.format(x=subject(p.title(lang)).lower() if lang == "fr" else subject(p.title(lang))),
                              "lang": lang, "keys": [p.key], "field": label})
    return items


def bootstrap(hits: list[bool], rounds: int = 2000, seed: int = 3) -> tuple[float, float, float]:
    rng = random.Random(seed)
    n = len(hits)
    if not n:
        return 0.0, 0.0, 0.0
    means = sorted(sum(rng.choice(hits) for _ in range(n)) / n for _ in range(rounds))
    return sum(hits) / n, means[int(0.025 * rounds)], means[int(0.975 * rounds)]


def write(items: list[dict], path: str | Path) -> None:
    Path(path).write_text(json.dumps(items, ensure_ascii=False, indent=1), encoding="utf-8")

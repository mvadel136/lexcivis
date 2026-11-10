import re
from functools import lru_cache
from importlib import resources

import yaml

from .text import normalize

_WORD = re.compile(r"[\w']+", re.UNICODE)


def _resource(name: str) -> dict:
    return yaml.safe_load(resources.files("lexcivis.resources").joinpath(name).read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def _lexicon() -> dict[str, str]:
    data = _resource("hassaniya.yaml")
    merged = {**data["arabic_script"], **data["latin_script"]}
    return {normalize(k): v for k, v in merged.items()}


@lru_cache(maxsize=1)
def _phrases() -> dict[str, str]:
    return {normalize(k): v for k, v in _resource("terms.yaml")["phrases"].items()}


def hassaniya_terms(text: str) -> list[str]:
    lexicon = _lexicon()
    return [w for w in _WORD.findall(normalize(text)) if w in lexicon]


def is_hassaniya(text: str) -> bool:
    return "گ" in text or bool(hassaniya_terms(text))


def expand(text: str) -> str:
    lexicon, norm = _lexicon(), normalize(text)
    extra = [lexicon[w] for w in _WORD.findall(norm) if w in lexicon]
    extra += [v for k, v in _phrases().items() if k in norm]
    return f"{text} {' '.join(extra)}" if extra else text

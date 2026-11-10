import importlib
import json
import re
from dataclasses import dataclass
from typing import Callable, Protocol

import httpx

from .settings import Settings
from .text import numbers, tokens


class ChatModel(Protocol):
    name: str

    def complete(self, system: str, user: str, max_tokens: int = 800) -> str: ...


class OpenAICompatible:
    def __init__(self, base_url: str, api_key: str, model: str, timeout: float = 60.0):
        self.name = model
        self.client = httpx.Client(base_url=base_url, timeout=timeout,
                                   headers={"Authorization": f"Bearer {api_key}"})
        self.model = model

    def complete(self, system: str, user: str, max_tokens: int = 800) -> str:
        r = self.client.post("/chat/completions", json={
            "model": self.model, "temperature": 0.2, "max_tokens": max_tokens,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]})
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"] or ""


class Plugged:
    def __init__(self, target: str):
        module, _, attr = target.partition(":")
        loaded = importlib.import_module(module)
        self.fn: Callable[[str, str, int], str] = getattr(loaded, attr)
        self.name = str(getattr(loaded, "MODEL", target))

    def complete(self, system: str, user: str, max_tokens: int = 800) -> str:
        return self.fn(system, user, max_tokens)


def chat_model(settings: Settings) -> ChatModel | None:
    backend = settings.llm_backend
    if backend == "none":
        return None
    if ":" in backend:
        return Plugged(backend)
    if not settings.llm_api_key:
        return None
    return OpenAICompatible(settings.llm_base_url, settings.llm_api_key, settings.llm_model)


def parse_json(text: str) -> dict | None:
    m = re.search(r"\{.*\}", text or "", re.S)
    if not m:
        return None
    try:
        value = json.loads(m.group(0))
    except json.JSONDecodeError:
        return None
    return value if isinstance(value, dict) else None


PLAIN_SYSTEM = {
    "fr": "Tu reformules une fiche administrative officielle pour un citoyen, en français simple, en 2 à 4 phrases courtes. "
          "Reprends les mots de la fiche. Garde chaque montant et chaque délai tels quels. N'ajoute aucun lieu, aucun service, "
          "aucune étape, aucun document, aucun conseil qui n'est pas écrit dans la fiche. Si une information manque, n'en parle pas.",
    "ar": "أعد صياغة بطاقة إدارية رسمية لمواطن بلغة عربية بسيطة في جملتين إلى أربع جمل قصيرة. استعمل كلمات البطاقة. "
          "احتفظ بكل مبلغ وكل مدة كما هي. لا تضف أي مكان أو مصلحة أو خطوة أو وثيقة أو نصيحة غير مكتوبة في البطاقة. "
          "إذا كانت معلومة ناقصة فلا تذكرها.",
}
GROUNDING = 0.75
_STOP = set("""vous votre vos pour avec dans cette sont être avoir faire doit devez peut pouvez aussi ainsi alors donc plus
moins tout tous toute toutes elle elles leur leurs dont comme mais entre après avant encore autre autres simple simplement
suffit suffira nécessaire nécessaires obtenir demander devrez pourrez permet permettent concerne concernée concernés
هذه هذا التي الذي الذين ذلك تلك عليك يجب يمكن يمكنك لكي حتى بعد قبل ايضا كذلك اذا بها لها فيها عليها منها مع على الى""".split())



_LIST_MARKER = re.compile(r"^\s*\d{1,2}[.)-]\s", re.M)


@dataclass
class Rewrite:
    text: str
    accepted: bool
    reason: str
    draft: str = ""


def _content(text: str) -> list[str]:
    return [w for w in tokens(text) if len(w) >= 5 and not w.isdigit() and w not in _STOP]


def grounding(draft: str, source: str) -> tuple[float, list[str]]:
    stems = {w[:5] for w in _content(source)}
    words = _content(draft)
    missing = sorted({w for w in words if w[:5] not in stems})
    supported = sum(1 for w in words if w[:5] in stems)
    return (supported / len(words) if words else 1.0), missing


def plain_language(model: ChatModel, answer) -> Rewrite:
    facts = "\n".join(f"{i.label}: {i.value}" for i in answer.items if not i.held)
    if not facts:
        return Rewrite("", False, "no published value to rephrase")
    try:
        draft = model.complete(PLAIN_SYSTEM[answer.lang], f"{answer.title}\n{facts}", max_tokens=500).strip()
    except Exception as exc:
        return Rewrite("", False, f"LLM unavailable ({type(exc).__name__})")
    if not draft:
        return Rewrite("", False, "empty rewrite")
    official = set(numbers(answer.values))
    used = set(numbers(_LIST_MARKER.sub("", draft)))
    added = sorted(used - official - set(numbers(answer.title)))
    if added:
        return Rewrite("", False, f"rejected: numbers not in the official record ({', '.join(added)})", draft)
    dropped = sorted(official - used)
    if dropped:
        return Rewrite("", False, f"rejected: official numbers left out ({', '.join(dropped)})", draft)
    share, missing = grounding(draft, f"{answer.title} {facts}")
    if share < GROUNDING:
        return Rewrite("", False, f"rejected: words not in the official record ({', '.join(missing[:6])})", draft)
    return Rewrite(draft, True, f"accepted: numbers kept, {share:.0%} of the wording comes from the record", draft)

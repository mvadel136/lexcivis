import re
from dataclasses import asdict, dataclass, field
from datetime import date

from .catalog import DISPLAY, Field, Procedure
from .dialect import is_hassaniya
from .intent import IntentClassifier
from .privacy import mask
from .quality import Verdicts, field_conflict
from .search.hybrid import Hit, HybridSearcher
from .text import detect_lang, numbers

OVERVIEW_FIELDS = (Field.DOCUMENTS, Field.FEE, Field.DELAY, Field.RECEPTION)
STALE_AFTER_MONTHS = 12
CLOSE_MARGIN = 0.15
VERIFY_DEPTH = 3
CHALLENGER_RATIO = 5.0
CLARIFY_BELOW = 0.01
_AMOUNT = re.compile(r"\d[\d\s.,]*\s*\(?\s*(?:mru|um|ouguiyas?|أوقية|اوقية|أو-ج|ا\.ج)", re.I)


def claimed_amounts(text: str) -> tuple[str, list[str]]:
    found = [numbers(m.group(0)) for m in _AMOUNT.finditer(text)]
    return _AMOUNT.sub(" ", text), sorted({n for group in found for n in group})


def cite(ref: dict) -> str:
    place = f"{ref['file']}, entry {ref['entry']}, {ref['lang'].upper()} record {ref['id']}"
    return f"{place}, field \"{ref['field']}\"" if ref.get("field") else place


def months_between(earlier: date, later: date) -> int:
    return (later.year - earlier.year) * 12 + later.month - earlier.month

MESSAGES = {
    "refused": {
        "fr": "Aucune procédure du fichier de référence ne correspond à cette question. Adressez-vous à l'administration concernée.",
        "ar": "لا يوجد إجراء في ملف المرجع يطابق هذا السؤال. يرجى مراجعة الإدارة المعنية.",
    },
    "held": {
        "fr": "Les versions officielles française et arabe ne donnent pas la même valeur. LexCivis ne choisit pas : l'administration doit confirmer.",
        "ar": "النسختان الرسميتان الفرنسية والعربية لا تعطيان القيمة نفسها. لا يختار LexCivis بدلاً منك: يجب أن تؤكد الإدارة.",
    },
    "missing": {"fr": "Non publié sur la fiche officielle.", "ar": "غير منشور في البطاقة الرسمية."},
    "other_lang": {"fr": "Valeur disponible seulement dans la version arabe.", "ar": "القيمة متوفرة فقط في النسخة الفرنسية."},
    "one_lang": {"fr": "Cette procédure n'est publiée qu'en arabe.", "ar": "هذا الإجراء منشور بالفرنسية فقط."},
    "stale": {"fr": "Fiche mise à jour le {d}. Elle peut avoir changé depuis.", "ar": "آخر تحديث للبطاقة في {d}. قد تكون تغيرت منذ ذلك الحين."},
    "pii": {"fr": "Vos données personnelles ont été masquées : ne les envoyez pas dans le chat.", "ar": "تم إخفاء بياناتك الشخصية: لا ترسلها في المحادثة."},
    "source": {"fr": "Source", "ar": "المصدر"},
    "clarify": {"fr": "Votre question peut correspondre à plusieurs procédures. Précisez laquelle :",
                "ar": "قد يتعلق سؤالك بعدة إجراءات. حدّد أيّها تقصد:"},
    "misfiled": {"fr": "La fiche officielle contient une valeur incohérente pour ce champ : elle doit être corrigée par l'administration.",
                 "ar": "تحتوي البطاقة الرسمية على قيمة غير متسقة في هذا الحقل: يجب أن تصححها الإدارة."},
    "claim_absent": {"fr": "Le montant {n} cité dans votre question ne figure pas dans la fiche officielle « {t} ». Ne payez pas sur la base d'un message non officiel.",
                     "ar": "المبلغ {n} المذكور في سؤالك غير موجود في البطاقة الرسمية «{t}». لا تدفع بناءً على رسالة غير رسمية."},
    "claim_present": {"fr": "Le montant {n} figure dans la fiche officielle « {t} ».",
                      "ar": "المبلغ {n} موجود في البطاقة الرسمية «{t}»."},
    "claim_unverified": {"fr": "Le montant {n} cité dans votre question ne peut pas être vérifié : aucune fiche officielle ne correspond. Ne payez rien sur la base d'un message non officiel.",
                         "ar": "لا يمكن التحقق من المبلغ {n} المذكور في سؤالك: لا توجد بطاقة رسمية مطابقة. لا تدفع أي شيء بناءً على رسالة غير رسمية."},
    "also": {"fr": "Procédures proches", "ar": "إجراءات قريبة"},
}


@dataclass
class Item:
    field: str
    label: str
    value: str
    source_lang: str
    source: dict
    held: bool = False
    fr_value: str = ""
    ar_value: str = ""
    ar_source: dict = field(default_factory=dict)


@dataclass
class Answer:
    status: str
    lang: str
    query: str
    hassaniya: bool
    intent: str
    intent_confidence: float
    procedure_key: str = ""
    title: str = ""
    source: dict = field(default_factory=dict)
    attachments: list = field(default_factory=list)
    ministry: str = ""
    last_update: str = ""
    items: list = field(default_factory=list)
    alternatives: list = field(default_factory=list)
    notes: list = field(default_factory=list)
    masked: list = field(default_factory=list)
    claims: list = field(default_factory=list)
    score: float = 0.0
    trace: dict = field(default_factory=dict)
    text: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @property
    def values(self) -> str:
        return "\n".join(f"{i.fr_value} {i.ar_value} {i.value}" for i in self.items)


@dataclass(frozen=True)
class Policy:
    refuse_below: float = 0.002
    verify_depth: int = VERIFY_DEPTH
    challenger_ratio: float = CHALLENGER_RATIO
    clarify_below: float = CLARIFY_BELOW
    stale_after_months: int = STALE_AFTER_MONTHS


class Composer:
    def __init__(self, searcher: HybridSearcher, intents: IntentClassifier, verdicts: Verdicts,
                 policy: Policy | float, today: date | None = None):
        self.searcher, self.intents, self.verdicts = searcher, intents, verdicts
        self.policy = policy if isinstance(policy, Policy) else Policy(refuse_below=policy)
        self.refuse_below = self.policy.refuse_below
        self.today = today or date.today()

    def answer(self, question: str, lang: str | None = None) -> Answer:
        text, masked = mask(question)
        lang = lang if lang in ("fr", "ar") else detect_lang(text)
        intent = self.intents.predict(text)
        search_text, claims = claimed_amounts(text)
        hits = self.searcher.search(search_text, lang, k=4, field=intent.field, verify_depth=self.policy.verify_depth)
        a = Answer("refused", lang, text, is_hassaniya(text), intent.label, round(intent.confidence, 3), masked=masked,
                   claims=claims)
        if masked:
            a.notes.append(MESSAGES["pii"][lang])
        best = self._choose(hits)
        a.trace = self._trace(hits)
        if best is None:
            a.score = hits[0].score if hits else 0.0
            a.notes[:0] = [MESSAGES["claim_unverified"][lang].format(n=n) for n in claims]
            a.text = self._render(a)
            return a
        rest = [h for h in hits if h is not best]
        seen = {best.procedure.title(lang).strip().lower()}
        close = []
        for h in rest:
            title = h.procedure.title(lang).strip().lower()
            if best.score - h.score < CLOSE_MARGIN and title not in seen:
                seen.add(title)
                close.append(h)
        a.alternatives = [{"key": h.procedure.key, "title": h.procedure.title(lang), "score": round(h.score, 4)} for h in close]
        a.score = round(best.score, 4)
        if intent.field is None and (best.support or 0) < self.policy.clarify_below and len(close) >= 2:
            a.status = "clarify"
            a.alternatives.insert(0, {"key": best.procedure.key, "title": best.procedure.title(lang), "score": a.score})
            a.text = self._render(a)
            return a
        self._fill(a, best.procedure, intent.field)
        self._check_claims(a, lang)
        a.text = self._render(a)
        return a

    def _choose(self, hits: list[Hit]) -> Hit | None:
        top = [h for h in hits[:self.policy.verify_depth] if h.support is None or h.support >= self.refuse_below]
        if not top:
            return None
        best = top[0]
        challenger = max(top, key=lambda h: h.support or 0.0)
        if challenger is not best and (challenger.support or 0) >= self.policy.challenger_ratio * max(best.support or 0, 1e-9):
            return challenger
        return best

    def _check_claims(self, a: Answer, lang: str) -> None:
        official = set(numbers(a.values))
        for n in a.claims:
            key = "claim_present" if n in official else "claim_absent"
            a.notes.insert(0, MESSAGES[key][lang].format(n=n, t=a.title))

    def _fill(self, a: Answer, p: Procedure, wanted: Field | None) -> None:
        record = p.record(a.lang)
        a.procedure_key, a.title, a.source, a.attachments = p.key, record.title, record.ref(), p.attachments
        a.ministry, a.last_update = record.ministry, record.last_update
        for f in ([wanted] if wanted else OVERVIEW_FIELDS):
            a.items.append(self._item(p, f, a.lang))
        if record.lang != a.lang:
            a.notes.append(MESSAGES["one_lang"][a.lang])
        if any(i.held for i in a.items):
            a.status = "held"
            a.notes.insert(0, MESSAGES["held"][a.lang])
        else:
            a.status = "answered"
        updated = record.updated_on
        if updated and months_between(updated, self.today) > self.policy.stale_after_months:
            a.notes.append(MESSAGES["stale"][a.lang].format(d=updated.strftime("%d/%m/%Y")))

    def _item(self, p: Procedure, f: Field, lang: str) -> Item:
        label = DISPLAY[f][1 if lang == "ar" else 0]
        conflict = field_conflict(p, f, self.verdicts)
        if conflict and conflict.status == "misfiled":
            return Item(f.value, f"{label} · {MESSAGES['misfiled'][lang]}", "", "fr+ar", p.fr.ref(f), True, conflict.fr,
                        conflict.ar, p.ar.ref(f))
        if conflict and conflict.status != "false_alarm":
            return Item(f.value, label, "", "fr+ar", p.fr.ref(f), True, conflict.fr, conflict.ar, p.ar.ref(f))
        primary = p.record(lang)
        value = primary.get(f)
        if value:
            return Item(f.value, label, value, primary.lang, primary.ref(f))
        other = p.ar if primary is p.fr else p.fr
        if other and other is not primary and other.get(f):
            return Item(f.value, f"{label} · {MESSAGES['other_lang'][lang]}", other.get(f), other.lang, other.ref(f))
        return Item(f.value, label, MESSAGES["missing"][lang], "", primary.ref(f))

    @staticmethod
    def _trace(hits: list[Hit]) -> dict:
        return {"candidates": [{"key": h.procedure.key, "rerank": None if h.rerank is None else round(h.rerank, 4),
                                "support": None if h.support is None else round(h.support, 4),
                                "lexical_rank": h.lexical_rank, "dense_rank": h.dense_rank} for h in hits]}

    @staticmethod
    def _render(a: Answer) -> str:
        if a.status == "refused":
            return "\n".join([MESSAGES["refused"][a.lang], *a.notes])
        if a.status == "clarify":
            return "\n".join([MESSAGES["clarify"][a.lang], *[f"- {x['title']}" for x in a.alternatives], *a.notes])
        lines = [a.title, ""]
        for i in a.items:
            if i.held:
                lines += [f"{i.label}:", f"  FR: {i.fr_value}", f"  AR: {i.ar_value}"]
            else:
                lines.append(f"{i.label}: {i.value}")
        lines += ["", *a.notes, f"{MESSAGES['source'][a.lang]}: {cite(a.source)}"]
        if a.alternatives:
            lines.append(f"{MESSAGES['also'][a.lang]}: " + " · ".join(x["title"] for x in a.alternatives))
        return "\n".join(lines)

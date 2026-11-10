import ast
import json
import re
from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from pathlib import Path


class Field(str, Enum):
    DOCUMENTS = "documents"
    FEE = "fee"
    DELAY = "delay"
    OFFICE = "office"
    RECEPTION = "reception"
    PROCESSING = "processing"
    DELIVERY = "delivery"
    COMPLAINTS = "complaints"
    USERS = "users"
    LEGAL_BASIS = "legal_basis"
    CONTACT = "contact"
    DESCRIPTION = "description"


SOURCE_LABELS = {
    Field.DOCUMENTS: ("Documents requis", "الوثائق المطلوبة"),
    Field.FEE: ("Frais afférents à la procédure", "الرسوم الواجب دفعها لانجاز المسطرة"),
    Field.DELAY: ("Délai de traitement", "مدة معالجة الطلب"),
    Field.OFFICE: ("Entité chargée de la procédure", "الجهة المكلفة بالمسطرة"),
    Field.RECEPTION: ("Entité chargée de la réception de la demande", "الجهة المكلفة باستقبال الطلب"),
    Field.PROCESSING: ("Entités chargées du traitement de la demande", "الجهات المكلفة بمعالجة الطلب"),
    Field.DELIVERY: ("Entité chargée de fournir la prestation demandée", "الجهة المكلفة بتسليم الخدمة"),
    Field.COMPLAINTS: ("Entité chargée de recevoir les réclamations", "الجهة المكلفة باستقبال التظلمات"),
    Field.USERS: ("Usagers de la procédure", "المستفيدون من الإجراء"),
    Field.LEGAL_BASIS: ("Bases juridiques et réglementaires de la procédure", "الأسس القانونية والتنظيمية للمسطرة"),
    Field.CONTACT: ("Contact", "للإتصال"),
    Field.DESCRIPTION: ("Description de la procédure ou du service", "وصف الإجراء أو الخدمة"),
}

DISPLAY = {
    Field.DOCUMENTS: ("Documents requis", "الوثائق المطلوبة"),
    Field.FEE: ("Frais", "الرسوم"),
    Field.DELAY: ("Délai de traitement", "مدة المعالجة"),
    Field.OFFICE: ("Administration responsable", "الجهة المسؤولة"),
    Field.RECEPTION: ("Où déposer la demande", "مكان إيداع الطلب"),
    Field.PROCESSING: ("Traitement de la demande", "معالجة الطلب"),
    Field.DELIVERY: ("Où retirer le document", "مكان تسليم الخدمة"),
    Field.COMPLAINTS: ("Réclamations", "التظلمات"),
    Field.USERS: ("Qui peut faire la demande", "المستفيدون"),
    Field.LEGAL_BASIS: ("Base juridique", "الأساس القانوني"),
    Field.CONTACT: ("Contact", "للاتصال"),
    Field.DESCRIPTION: ("Description", "الوصف"),
}

_LABEL_TO_FIELD = {label: f for f, labels in SOURCE_LABELS.items() for label in labels}
SOURCE_FILE = "data/procedures.json"


@dataclass(frozen=True)
class Record:
    lang: str
    id: str
    entry: int
    title: str
    category: str
    ministry: str
    last_update: str
    fields: dict = field(default_factory=dict)
    related: tuple = ()
    attachments: tuple = ()

    def get(self, f: Field) -> str:
        return (self.fields.get(f) or "").strip()

    def ref(self, f: Field | None = None) -> dict:
        label = SOURCE_LABELS[f][1 if self.lang == "ar" else 0] if f else ""
        return {"file": SOURCE_FILE, "entry": self.entry, "lang": self.lang, "id": self.id, "field": label}

    @property
    def updated_on(self) -> date | None:
        m = re.match(r"(\d{2})/(\d{2})/(\d{4})", self.last_update or "")
        return date(int(m[3]), int(m[2]), int(m[1])) if m else None


@dataclass(frozen=True)
class Procedure:
    key: str
    fr: Record | None
    ar: Record | None

    @property
    def attachments(self) -> list[dict]:
        seen, out = set(), []
        for r in self.records:
            for a in r.attachments:
                if a["file"] not in seen:
                    seen.add(a["file"])
                    out.append({**a, "lang": r.lang})
        return out

    def record(self, lang: str) -> Record | None:
        primary = self.ar if lang == "ar" else self.fr
        return primary or self.fr or self.ar

    def title(self, lang: str) -> str:
        r = self.record(lang)
        return r.title if r else ""

    @property
    def records(self) -> list[Record]:
        return [r for r in (self.fr, self.ar) if r]


def _literal(raw):
    if isinstance(raw, (dict, list)):
        return raw
    try:
        return ast.literal_eval(raw or "{}")
    except (ValueError, SyntaxError):
        return {}


def _record(raw: dict | None, entry: int) -> Record | None:
    if not raw:
        return None
    fields = {}
    for label, value in _literal(raw.get("fields")).items():
        f = _LABEL_TO_FIELD.get(label.strip())
        if f and str(value).strip():
            fields[f] = str(value).strip()
    related = tuple(r.get("id", "") for r in _literal(raw.get("related_procedures")) or [] if isinstance(r, dict))
    attachments = tuple(a for a in _literal(raw.get("attachments")) or [] if isinstance(a, dict) and a.get("file"))
    return Record(raw.get("lang", ""), str(raw.get("id", "")), entry, (raw.get("title") or "").strip(),
                  (raw.get("category") or "").strip(), (raw.get("ministry") or "").strip(),
                  raw.get("last_update") or "", fields, related, attachments)


class Catalog:
    def __init__(self, procedures: list[Procedure]):
        self.procedures = procedures
        self._by_key = {p.key: p for p in procedures}
        self._by_record = {(r.lang, r.id): p for p in procedures for r in p.records}

    @classmethod
    def load(cls, path: str | Path) -> "Catalog":
        rows = json.loads(Path(path).read_text(encoding="utf-8"))
        procedures = []
        for entry, row in enumerate(rows, start=1):
            fr, ar = _record(row.get("fr"), entry), _record(row.get("ar"), entry)
            key = f"fr{fr.id}" if fr else f"ar{ar.id}"
            procedures.append(Procedure(key, fr, ar))
        return cls(procedures)

    def __len__(self) -> int:
        return len(self.procedures)

    def __iter__(self):
        return iter(self.procedures)

    def get(self, key: str) -> Procedure | None:
        return self._by_key.get(key)

    def by_fr_id(self, fr_id: str) -> Procedure | None:
        return self._by_record.get(("fr", str(fr_id)))

    @property
    def pairs(self) -> list[Procedure]:
        return [p for p in self.procedures if p.fr and p.ar]

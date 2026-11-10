import re
import unicodedata

_AR_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹٫٬", "01234567890123456789.,")
_AR_DIACRITICS = re.compile(r"[ؐ-ًؚ-ٰٟۖ-ۭـ]")
_AR_LETTERS = str.maketrans({"أ": "ا", "إ": "ا", "آ": "ا", "ٱ": "ا", "ى": "ي", "ئ": "ي", "ؤ": "و", "ة": "ه", "گ": "ق", "ڤ": "ف", "ڨ": "ق"})
_THOUSANDS = re.compile(r"(?<=\d)[ .,  ](?=\d{3}(?!\d))")
_NUMBER = re.compile(r"\d+(?:[.,]\d+)?")
_ARABIC = re.compile(r"[؀-ۿ]")
_TOKEN = re.compile(r"[\w]+", re.UNICODE)


def is_arabic(text: str) -> bool:
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return False
    return sum(1 for c in letters if _ARABIC.match(c)) / len(letters) > 0.3


def detect_lang(text: str) -> str:
    return "ar" if is_arabic(text) else "fr"


def strip_accents(text: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", text) if not unicodedata.combining(c))


def normalize_ar(text: str) -> str:
    text = _AR_DIACRITICS.sub("", text.translate(_AR_DIGITS))
    return text.translate(_AR_LETTERS)


def normalize(text: str) -> str:
    text = (text or "").translate(_AR_DIGITS).lower()
    text = normalize_ar(text)
    text = strip_accents(text)
    text = text.replace("’", "'").replace("œ", "oe")
    return re.sub(r"\s+", " ", text).strip()


def tokens(text: str) -> list[str]:
    out = []
    for tok in _TOKEN.findall(normalize(text)):
        if len(tok) < 2 and not tok.isdigit():
            continue
        if _ARABIC.match(tok) and tok.startswith("ال") and len(tok) > 4:
            out.append(tok[2:])
        out.append(tok)
    return out


def numbers(text: str | None) -> list[str]:
    s = (text or "").translate(_AR_DIGITS)
    s = _THOUSANDS.sub("", _THOUSANDS.sub("", s))
    return sorted({n.replace(",", ".") for n in _NUMBER.findall(s)})


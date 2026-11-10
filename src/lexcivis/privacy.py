import re

_NNI = re.compile(r"(?<!\d)\d{10}(?!\d)|(?i:\bnni\b|الرقم الوطني|رقم التعريف)\s*[:#]?\s*\d[\d .-]{8,14}\d")
_PHONE = re.compile(r"(?<!\d)(?<!\d[.,])(?:\+?222[ .-]?)?[234]\d(?:\d{6}|(?:[ .-]\d{2}){3})(?!\d|[.,]\d)(?!\s*(?:mru|um|ouguiya|أوقية))", re.I)
_EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
_DATE = re.compile(r"(?<!\d)\d{1,2}[/.-]\d{1,2}[/.-](?:19|20)\d{2}(?!\d)")
_NAME = re.compile(r"(?i:je m['’]appelle|mon nom est|mon nom:)\s+([A-ZÀ-Ý][\w'’-]+(?:\s+(?:ould|mint|ben|bint|[A-ZÀ-Ý][\w'’-]+)){0,4})"
                   r"|(?:اسمي|أنا اسمي)\s+([\u0600-\u06ff]+(?:\s+(?!\u0648[\u0623\u0627\u062a\u064a\u0646])[\u0600-\u06ff]+){0,3})")

PATTERNS = (("national_id", _NNI, "[NNI]"), ("phone", _PHONE, "[TEL]"), ("email", _EMAIL, "[EMAIL]"), ("date", _DATE, "[DATE]"))


def _mask_name(match: re.Match) -> str:
    name = match.group(1) or match.group(2)
    return match.group(0).replace(name, "[NOM]")


def mask(text: str) -> tuple[str, list[str]]:
    found = []
    if _NAME.search(text):
        found.append("name")
        text = _NAME.sub(_mask_name, text)
    for name, pattern, token in PATTERNS:
        if pattern.search(text):
            found.append(name)
            text = pattern.sub(token, text)
    return text, found

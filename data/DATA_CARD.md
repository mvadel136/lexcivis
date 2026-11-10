# Data card: Mauritania administrative procedures

## Source and scope
- **Source:** Mauritania's public administrative procedures, one record per language, with the legal texts and forms
  attached to them.
- **File:** `procedures.json`. 836 procedures from 31 administrations: 812 French/Arabic pairs, 19 French-only,
  5 Arabic-only. Field values are used as published. The web links (`url`, `other_lang_url`, and one Arabic contact
  field that held only a web address) were removed, and each attachment points to its file in `documents/`.
- **Citation:** every answer cites `procedures.json`, the entry number (1 to 836), the language version, the record id
  and the field.
- **Attachments:** `documents/` holds the 98 distinct files behind the 242 attachments (see below).
- **Record fields** (one record per language): title, category, ministry, last update, required documents, fee,
  processing delay, responsible entity, reception, processing, delivery, complaints, users, legal basis, contact,
  description, related procedures.

## Derived files (`lexcivis profile`)
- `derived/procedures_normalized.jsonl`, one row per procedure, with:
  - the fee type (free, amount, percentage, depends, unspecified, missing, other) and the amounts in MRU (old
    ouguiya "UM" divided by 10, and flagged);
  - the delay as a range in days, and its type (duration, not a duration, missing, other);
  - the number of required documents in French and in Arabic;
  - whether a legal basis is present, and whether the contact is specific or a generic ministry address;
  - a completeness score over six key fields, and the confirmed French/Arabic conflicts.
- `derived/data_profile.json` holds the aggregate figures below.
- `quality/verdicts.json` holds the verdict (confirmed, false alarm, misfiled) and reason for each of the 94 automatic French/Arabic flags.

## Attached legal texts and forms (`documents/`, `lexcivis library`)
- `manifest.json`: for each document, its SHA-256, every original file name, the titles used by the procedures, the
  procedures that attach it, the page count and how many pages were read by OCR. Broken attachments are listed.
- `files/`: one copy of each document, named by the first 16 hex digits of its SHA-256. `rendered/`: Word forms
  converted to PDF for display.
- `pages/`: the text of every page, from the PDF text layer or from Tesseract OCR (French + Arabic, 300 dpi) when a page
  has no text. OCR text can contain errors; the page image is the reference.

| Measure | Value |
|---|---|
| Procedures with attachments | 106 |
| Attached files / distinct documents | 242 / 98 (55 legal texts, 43 forms) |
| Pages / pages read by OCR | 1,630 / 200 (28 documents fully scanned) |
| Copies of the same file under another name | 141 |
| Attachments that are not documents | 3 (macOS `._` metadata files) |
| Titles that are a phone-scanner file name | 2 ("CamScanner …"), one attached to 16 procedures |

## What the data says
| Measure | Value |
|---|---|
| Fee | 327 free, 193 with an amount (median 2,000 MRU, max 3,000,000 MRU), 158 empty, 64 "non spécifié", 55 "depends", 37 free text, 2 percentages |
| Delay | 507 durations; 158 that are not a duration ("à la demande", "relatif"…); 74 empty |
| Published delays | same day 100, ≤ 2 days 102, ≤ 1 week 114, ≤ 1 month 115, ≤ 3 months 56, longer 20 |
| Real values filled (French / Arabic) | documents 94% / 94%, fee 73% / 73%, delay 81% / 77%, legal basis 61% / 63%, description 29% / 32% |
| French/Arabic conflicts on fee or delay | 54 procedures (94 flags: 63 confirmed, 28 false alarms, 3 misfiled fields) |
| Document lists of different length in French and Arabic | 190 pairs |
| No legal basis in either language | 279 pairs |
| Only a generic ministry e-mail as contact | 506 procedures |
| Related-procedure links pointing to missing records | 104 of 13,160 |
| Same title published twice | 11 groups (23 records) |
| Fields filled in the wrong place | e.g. `fr1840` (Arabic fee and delay swapped), `fr214` (decree in the Arabic fee field) |
| Last update | 2023: 527, 2024: 190, 2025: 119; no record has a validity period |
| Least complete administrations (≥ 5 procedures) | Vocational Training 47%, Land Registry 53%, Food Security 58%, Islamic Affairs 62% (most complete: Livestock 100%, Water 95%, Justice 94%) |

## Known limits
- The fee and delay parsers are rule-based. Their output is checked by the tests in `tests/test_profile.py`, but a
  share of free-text values stays "other".
- A French/Arabic conflict shows that the two versions differ. It cannot say which one is correct.
- The verdicts were made by reading both texts. A review by the publishing administrations is the next step.

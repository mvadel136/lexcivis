from lexcivis.catalog import Field
from lexcivis.dialect import expand, is_hassaniya
from lexcivis.privacy import mask
from lexcivis.quality import Verdicts, audit, conflicts
from lexcivis.text import detect_lang, normalize, numbers


def test_numbers_normalise_separators_and_arabic_digits():
    assert numbers("600 000 MRU") == numbers("600.000 أوقية") == ["600000"]
    assert numbers("خمسة عشر(١٥) يوما") == ["15"]


def test_arabic_normalisation():
    assert normalize("إجراءات الأسرة") == normalize("اجراءات الاسره")
    assert detect_lang("ما هي الوثائق؟") == "ar"
    assert detect_lang("Quels documents ?") == "fr"


def test_catalog_maps_every_field(catalog):
    assert len(catalog) == 836
    assert len(catalog.pairs) == 812
    p = catalog.by_fr_id("183")
    assert p.fr.get(Field.FEE) == "Timbre: 50 MRU"
    assert "20" in p.ar.get(Field.FEE)


def test_conflict_detected_and_confirmed(catalog, verdicts):
    found = conflicts(catalog.by_fr_id("183"), verdicts)
    assert [(c.field, c.status) for c in found] == [("fee", "confirmed")]


def test_false_alarm_kept_out(catalog, verdicts):
    found = conflicts(catalog.by_fr_id("685"), verdicts)
    assert all(c.status == "false_alarm" for c in found)


def test_audit_counts(catalog, verdicts):
    r = audit(catalog, verdicts)
    assert (r.flagged, r.confirmed, r.false_alarms, r.misfiled) == (94, 63, 28, 3)
    assert r.procedures_with_confirmed_conflict == 54
    assert r.no_legal_basis == 279
    assert ["fr161", "fr2009"] in r.duplicate_titles


def test_unchecked_flags_stay_flagged(catalog):
    r = audit(catalog, Verdicts())
    assert r.flagged == 94 and r.confirmed == 0


def test_free_versus_paid_is_a_conflict(catalog, verdicts):
    found = conflicts(catalog.by_fr_id("283"), verdicts)
    assert ("fee", "confirmed") in [(c.field, c.status) for c in found]


def test_only_fee_and_delay_can_hold(composer):
    for key in ("fr24", "fr113"):
        p = composer.searcher.catalog.get(key)
        assert all(not composer._item(p, f, "fr").held for f in Field if f not in (Field.FEE, Field.DELAY))


def test_mask_removes_values():
    text, found = mask("NNI 1234567890, tel +222 22 33 44 55, a@b.mr")
    assert "1234567890" not in text and "44 55" not in text and "a@b.mr" not in text
    assert found == ["national_id", "phone", "email"]


def test_misfiled_field_is_held(composer):
    p = composer.searcher.catalog.get("fr1840")
    item = composer._item(p, Field.FEE, "fr")
    assert item.held and "incohérente" in item.label


def test_mask_names_and_dates():
    text, found = mask("Je m'appelle Ahmed Ould Mohamed, né le 12/03/1990")
    assert "Ahmed" not in text and "1990" not in text and found == ["name", "date"]
    assert mask("اسمي أحمد ولد محمد وأريد جواز سفر")[0] == "اسمي [NOM] وأريد جواز سفر"


def test_mask_keeps_fees():
    assert mask("frais 2000 4000 MRU")[1] == []
    assert mask("NNI 1234 567 890")[1] == ["national_id"]


def test_hassaniya_expansion():
    q = "شنهو لوراق الِّ لازمين باش نخرج بطاگة التعريف"
    assert is_hassaniya(q)
    assert "الوثائق" in expand(q)
    assert not is_hassaniya("Quels sont les documents requis ?")


def test_standard_arabic_is_not_tagged_hassaniya():
    assert not is_hassaniya("ما هي الوثائق المطلوبة لاستخراج بطاقة التعريف الوطنية؟")
    assert is_hassaniya("گداش تجديد رخصة السياقة؟")

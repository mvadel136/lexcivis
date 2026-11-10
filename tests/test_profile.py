from lexcivis.profile import delay_days, delay_kind, documents_count, fee_kind, profile


def test_fee_kinds():
    assert fee_kind("600 000 MRU") == ("amount", [600000.0], False)
    assert fee_kind("3000(MRU)")[1] == [3000.0]
    assert fee_kind("5 000 UM") == ("amount", [500.0], True)
    assert fee_kind("Gratuit")[0] == "free"
    assert fee_kind("مجانا")[0] == "free"
    assert fee_kind("Non spécifié")[0] == "unspecified"
    assert fee_kind("Montant fixé par délibération du conseil municipal")[0] == "depends"
    assert fee_kind("")[0] == "missing"


def test_delays_in_days():
    assert delay_days("45 jours") == (45, 45)
    assert delay_days("24 heures") == (1, 1)
    assert delay_days("De 2 à 5 jours") == (5, 5) or delay_days("De 2 à 5 jours")[1] == 5
    assert delay_days("خمسة عشر(15) يوما") == (15, 15)
    assert delay_days("Immédiat") == (0, 0)
    assert delay_days("3 mois") == (90, 90)
    assert delay_kind("Non spécifié") == "not a duration"
    assert delay_kind("A la demande") == "not a duration"


def test_documents_count():
    assert documents_count("• Présenter le numéro national • Soumettre la demande") == 2
    assert documents_count("- Une demande; - Ancien permis; - Copie pièce d'identité") == 3


def test_profile_totals(catalog, verdicts):
    report, rows = profile(catalog, verdicts)
    assert report["procedures"] == len(rows) == 836
    assert sum(report["fee_kinds"].values()) == 836
    assert report["related_links"]["broken"] > 0
    assert 0 < report["completeness_mean"] <= 1


def test_benchmark_generation_is_answerable_and_reproducible(catalog):
    from lexcivis.benchmark import answerable, generate, subject
    from lexcivis.catalog import Field

    a = generate(catalog, "data/eval/benchmark_v2_templates.yaml", per_cell=3, seed=5)
    b = generate(catalog, "data/eval/benchmark_v2_templates.yaml", per_cell=3, seed=5)
    assert a == b and len(a) == 30
    for item in a:
        p = catalog.get(item["keys"][0])
        assert answerable(p.record(item["lang"]), Field(item["field"]))
    assert subject("Demande de délivrance de passeport (Titres sécurisés)") == "délivrance de passeport"


def test_bootstrap_interval_contains_the_mean():
    from lexcivis.benchmark import bootstrap

    value, low, high = bootstrap([True] * 80 + [False] * 20)
    assert value == 0.8 and low < value < high

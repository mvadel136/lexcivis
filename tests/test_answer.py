from lexcivis.catalog import Field
from lexcivis.llm import plain_language


class FixedModel:
    name = "fixed"

    def __init__(self, reply):
        self.reply = reply

    def complete(self, system, user, max_tokens=800):
        return self.reply


def test_intent_predicts_fee(intents):
    assert intents.predict("Combien coûte le passeport ?").label == "fee"
    assert intents.predict("ما هي الوثائق المطلوبة لجواز السفر؟").label == "documents"


def test_answer_copies_official_value(composer, catalog):
    a = composer.answer("Combien coûte le renouvellement de permis de conduire ?")
    assert a.status == "answered"
    p = catalog.get(a.procedure_key)
    assert all(i.value == p.record("fr").get(Field(i.field)) for i in a.items)


def test_conflicting_fee_is_held(composer):
    a = composer.answer("Combien coûte le timbre pour des renseignements sur un titre foncier ?")
    assert a.procedure_key == "fr183"
    assert a.status == "held"
    held = [i for i in a.items if i.held]
    assert held and "50" in held[0].fr_value and "20" in held[0].ar_value


def test_personal_data_never_reaches_the_answer(composer):
    a = composer.answer("Mon NNI est 1234567890, comment renouveler ma carte d'identité ?")
    assert "1234567890" not in a.query and "national_id" in a.masked


def test_claimed_amount_is_checked(composer):
    from lexcivis.answer import claimed_amounts

    assert claimed_amounts("La carte coûte 5000 MRU, c'est vrai ?")[1] == ["5000"]
    a = composer.answer("Le renouvellement du permis de conduire coûte maintenant 9999 MRU, c'est vrai ?")
    assert a.claims == ["9999"] and any("9999" in n and "ne figure pas" in n for n in a.notes)


def test_refusal_still_warns_about_a_claimed_amount(composer):
    a = composer.answer("Le prix de la recette du couscous est 700 MRU, c'est vrai ?")
    assert a.status == "refused" and any("700" in n for n in a.notes)


def test_off_topic_is_refused(composer):
    assert composer.answer("Quelle est la recette du couscous traditionnel ?").status == "refused"


def test_plain_language_guards(composer):
    a = composer.answer("Combien coûte le renouvellement de permis de conduire ?")
    official = a.items[0].value
    rejected = plain_language(FixedModel("Le permis coûte 9999 MRU."), a)
    assert not rejected.accepted and rejected.text == "" and "9999" in rejected.reason
    dropped = plain_language(FixedModel("Le renouvellement du permis de conduire se paie en timbres fiscaux."), a)
    assert not dropped.accepted and "left out" in dropped.reason
    invented = plain_language(FixedModel(f"Rendez-vous à la préfecture avec vos pièces d'identité. {official}"), a)
    assert not invented.accepted and "words not in the official record" in invented.reason
    faithful = plain_language(FixedModel(f"Renouvellement du permis de conduire : {official}."), a)
    assert faithful.accepted


class BrokenModel:
    name = "broken"

    def complete(self, system, user, max_tokens=800):
        raise TimeoutError()


def test_llm_failure_keeps_the_official_answer(composer):
    a = composer.answer("Combien coûte le renouvellement de permis de conduire ?")
    r = plain_language(BrokenModel(), a)
    assert not r.accepted and "unavailable" in r.reason and a.text

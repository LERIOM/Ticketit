"""Masquage : aucune donnée personnelle du jeu de test ne reste dans le texte masqué,
les identifiants techniques sont extraits, les pseudonymes sont réversibles."""
import pytest

from app.security.masking import Masker, resolve_action_param, unmask

# (langue, texte, données personnelles qui ne doivent jamais apparaître)
PII_CASES = [
    ("fr", "Bonjour, je suis Jean Dupont, mon VPN ne marche plus.", ["Jean Dupont"]),
    ("fr", "Contactez-moi au 06 12 34 56 78 ou sur jean.dupont@exemplia.fr.",
     ["06 12 34 56 78", "jean.dupont@exemplia.fr"]),
    ("fr", "Mon poste a l'adresse 10.0.3.27 et celui de Pierre Martin 192.168.1.40.",
     ["10.0.3.27", "Pierre Martin", "192.168.1.40"]),
    ("fr", "Appeler Mme Sophie Leroy au +33 1 23 45 67 89 pour l'imprimante.",
     ["Sophie Leroy", "+33 1 23 45 67 89"]),
    ("fr", "Le compte j.martin a reçu un mail de phishing envoyé à j.martin@exemplia.fr.",
     ["j.martin@exemplia.fr"]),
    ("en", "Hi, this is Sarah Connor from HR, call me at +33 6 98 76 54 32.",
     ["Sarah Connor", "+33 6 98 76 54 32"]),
    ("en", "My manager John Smith (john.smith@exemplia.fr) approved the request.",
     ["John Smith", "john.smith@exemplia.fr"]),
    ("en", "Server 172.16.4.20 cannot reach the file share, ping from 10.1.2.3 fails.",
     ["172.16.4.20", "10.1.2.3"]),
    ("fr", "Bonjour,\nMarie Curie du labo signale que Outlook plante.\nCordialement", ["Marie Curie"]),
    ("fr", "Tél : 01.44.55.66.77 — Paul Durand, bureau 204.", ["01.44.55.66.77", "Paul Durand"]),
]


@pytest.fixture(scope="module")
def masker():
    return Masker()


@pytest.mark.parametrize("lang,text,pii", PII_CASES)
def test_no_pii_left(masker, lang, text, pii):
    masked = masker.mask(text, lang).text
    for value in pii:
        assert value not in masked, masked


@pytest.mark.parametrize("lang,text,pii", PII_CASES)
def test_reversible(masker, lang, text, pii):
    r = masker.mask(text, lang)
    assert unmask(r.text, r.mapping) == text


def test_technical_identifiers_extracted_and_hidden(masker):
    text = ("12 échecs SSH depuis 203.0.113.5 sur SRV-WEB-01, puis j.martin s'est connecté "
            "depuis PC-COMPTA-07 ; scan depuis 198.51.100.23.")
    r = masker.mask(text, "fr")
    assert r.entities.external_ips == ["203.0.113.5", "198.51.100.23"]
    assert r.entities.hostnames == ["SRV-WEB-01", "PC-COMPTA-07"]
    assert r.entities.usernames == ["j.martin"]
    for value in ("203.0.113.5", "SRV-WEB-01", "j.martin", "PC-COMPTA-07"):
        assert value not in r.text


def test_same_value_same_placeholder(masker):
    r = masker.mask("Jean Dupont a appelé. Jean Dupont rappellera depuis 10.0.0.5 et 10.0.0.5.", "fr")
    assert r.text.count("<PERSONNE_1>") == 2 and r.text.count("<IP_INT_1>") == 2


def test_privileged_account_in_context(masker):
    r = masker.mask("Merci de désactiver le compte admin.", "fr")
    assert r.entities.usernames == ["admin"] and "admin" not in r.text


def test_known_structured_values(masker):
    r = masker.mask("Compte visé : root. Hôte : web-legacy.", "fr",
                    known=[("root", "USERNAME"), ("web-legacy", "HOSTNAME")])
    assert r.entities.usernames == ["root"] and r.entities.hostnames == ["web-legacy"]


def test_product_names_not_masked(masker):
    text = "Alerte Wazuh : Outlook et Microsoft Teams plantent."
    assert masker.mask(text, "fr").text == text


def test_action_params_resolve_only_technical_placeholders():
    mapping = {"<IP_EXT_1>": "203.0.113.5", "<PERSONNE_1>": "Jean Dupont",
               "<IP_INT_1>": "10.0.0.12", "<COMPTE_1>": "j.martin"}
    assert resolve_action_param("<IP_EXT_1>", mapping) == "203.0.113.5"
    assert resolve_action_param("<COMPTE_1>", mapping) == "j.martin"
    assert resolve_action_param("<PERSONNE_1>", mapping) is None     # donnée personnelle
    assert resolve_action_param("<IP_INT_1>", mapping) is None       # IP interne : jamais une cible
    assert resolve_action_param("203.0.113.9", mapping) is None      # valeur inventée par le LLM
    assert resolve_action_param("<IP_EXT_9>", mapping) is None       # pseudonyme inexistant


# ------------------------------------------- relecture du bloc D (2026-10-27)

EN_PII_CASES = [
    ("Hi, I'm John Smith, call me at (555) 123-4567 or +1 415 555 0100.",
     ["John Smith", "(555) 123-4567", "+1 415 555 0100"]),
    ("my name is sarah connor and my laptop won't boot", ["sarah connor"]),
    ("Please contact Dr. Emily Watson (emily.watson@acme.com) about the outage.",
     ["Emily Watson", "emily.watson@acme.com"]),
    ("User jsmith cannot log in to the VPN from 192.168.1.20.", ["jsmith", "192.168.1.20"]),
]


@pytest.mark.parametrize("text,pii", EN_PII_CASES)
def test_no_pii_left_english(masker, text, pii):
    r = masker.mask(text, "en")
    for value in pii:
        assert value not in r.text, r.text
    assert unmask(r.text, r.mapping) == text


def test_parenthesis_kept_outside_placeholder(masker):
    r = masker.mask("Bonjour, je suis Jean Dupont (06 12 34 56 78), merci.", "fr")
    assert "(<TEL_1>)" in r.text and r.mapping["<TEL_1>"] == "06 12 34 56 78"


def test_balanced_parenthesis_stays_in_phone(masker):
    r = masker.mask("Call me at (555) 123-4567 please.", "en")
    assert "(555) 123-4567" in r.mapping.values()


@pytest.mark.parametrize("text,user", [
    ("User jsmith cannot log in.", "jsmith"),
    ("username: mlopez2", "mlopez2"),
    ("Please unlock account j_doe today.", "j_doe"),
    ("Reset the account for kwilliams, thanks.", "kwilliams"),
    ("Le compte de jdupont est bloqué.", "jdupont"),
])
def test_username_without_dot(masker, text, user):
    r = masker.mask(text, "en")
    assert r.entities.usernames == [user] and user not in r.text


@pytest.mark.parametrize("text", [
    "My account is locked since this morning.",
    "Login failed three times.",
    "The user cannot connect to the portal.",
    "The user profile page is broken.",
    "Mon compte est bloqué depuis ce matin.",
    "Alerte Wazuh : compte visé : root.",
])
def test_common_words_after_keyword_not_masked_as_user(masker, text):
    r = masker.mask(text, "en")
    assert not [u for u in r.entities.usernames if u != "root"], r.mapping

"""Masquage des données personnelles et des identifiants techniques, dès l'ingestion.

Deux familles, remplacées par des pseudonymes réversibles (`<PERSONNE_1>`…) :
- données personnelles (Presidio + spaCy) : noms, e-mails, téléphones, IP internes ;
- identifiants techniques utiles aux actions (regex déterministes) : IP externes,
  noms de poste, comptes. Ils sortent du texte envoyé au LLM et vont dans
  `Ticket.entities` ; le LLM ne manipule que des pseudonymes, le code les résout.

La table pseudonyme -> valeur reste côté serveur (security/vault.py).
"""
import ipaddress
import re
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Literal

from ..config import settings
from ..models import TechnicalEntities

Lang = Literal["fr", "en"]

PREFIX = {
    "PERSON": "PERSONNE", "EMAIL_ADDRESS": "EMAIL", "PHONE_NUMBER": "TEL",
    "INTERNAL_IP": "IP_INT", "EXTERNAL_IP": "IP_EXT", "HOSTNAME": "HOTE", "USERNAME": "COMPTE",
}
# Pseudonymes que le code accepte de résoudre en paramètre d'action.
ACTIONABLE_PREFIXES = ("IP_EXT", "HOTE", "COMPTE")
PLACEHOLDER_RE = re.compile(r"<(" + "|".join(PREFIX.values()) + r")_(\d+)>")

_INTERNAL_NETS = [ipaddress.ip_network(n) for n in (
    "10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16", "127.0.0.0/8",
    "169.254.0.0/16", "0.0.0.0/8", "100.64.0.0/10")]

_IPV4 = re.compile(r"(?<!\d)(?<!\d\.)(?:\d{1,3}\.){3}\d{1,3}(?!\d|\.\d)")
# Convention de nommage des actifs Exemplia : SRV-WEB-01, PC-COMPTA-07, DC-01…
_HOST = re.compile(r"\b(?:SRV|PC|DC|LT|WS|FW|NAS|SW|RTR|VM)-[A-Z0-9]+(?:-[A-Z0-9]+)*"
                   r"(?:\.[a-z0-9-]+\.(?:local|lan|corp|fr|com))?\b")
_PHONE_FR = re.compile(r"(?<!\d)(?:\+33\s?|0)[1-9](?:[\s.-]?\d{2}){4}(?!\d)")
_EMAIL = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
_USER = [
    re.compile(r"(?<![\w.@-])[a-z]\.[a-z]{2,}(?:-[a-z]+)?(?![\w@-]|\.[a-z])"),     # j.martin
    re.compile(r"\bsvc-[a-z0-9-]+\b"),                                            # comptes de service
    re.compile(r"(?i)\b(?:compte|account|utilisateur|user|login|identifiant)\s+(?:de\s+l'|de\s+|d')?"
               r"[«\"']?\s*(admin|administrateur|administrator|root|guest|invit[ée])\b"),
]
# Identifiant sans point (jsmith, mlopez2, j_doe) juste après un mot-clé de compte.
# Gardé s'il est en minuscules et n'est pas un mot courant : en cas de doute on masque
# (une donnée personnelle qui fuit vers le LLM coûte plus cher qu'un mot masqué en trop).
_CTX_USER = re.compile(
    r"(?i)\b(?:user(?:name)?|user\s*id|account|login|logon|uid|compte|utilisateur|identifiant)\b"
    r"\s*(?:[:=]|\b(?:is|est|named|nommé|for|of|pour|de|du)\b)?\s*[«\"'`]?\s*"
    r"([A-Za-z][A-Za-z0-9._-]{1,30}[A-Za-z0-9])(?![\w@-]|\.\w)")
_COMMON = set("""
a an the my our your his her their its this that these those some any no not all every each
is are was were be been being am has have had does do did can cannot cant could will would
should may might must shall to for from with without in on at of by into onto about as and or
but if then than so via per new old same other another more most less again also only just
still yet already now today yesterday when while after before during since until
account accounts user users username usernames name names id ids login logins logon
logout session sessions password passwords credential credentials pin mfa sso otp token
settings setting profile profiles page pages portal portals interface manager management
access details detail information info data request requests issue issues problem problems
error errors failure failed fails fail failing attempt attempts activity creation created
create delete deleted deletion disabled disable enabled enable locked lock lockout unlock
unlocked expired expiry reset blocked block suspended verification validation verified
authentication authorization permissions permission rights role roles group groups team
support service services team members member status type list count number base level
owner owners admins administrators guest guests root admin administrator
cannot unable trying tried try keeps keep seems seem appears appear stopped stop
experience guide documentation policy policies setup configuration config section menu
here there which who whom whose what where why how it he she they we you i me him them
compte comptes utilisateur utilisateurs identifiant identifiants mot passe session
le la les un une des du de au aux ce cet cette ces mon ma mes ton ta tes son sa ses notre
votre leur leurs est sont était été être a ont avait pas plus ne n et ou mais donc car
qui que quoi dont où pour par sur sous dans avec sans chez vers
bloqué bloquée verrouillé verrouillée désactivé désactivée expiré expirée suspendu
accès paramètres profil portail problème demande erreur échec
visé visée ciblé ciblée concerné concernée target targeted affected impacted compromised
""".split())


@dataclass
class Span:
    start: int
    end: int
    kind: str
    score: float


@dataclass
class MaskResult:
    text: str
    mapping: dict[str, str] = field(default_factory=dict)       # pseudonyme -> valeur d'origine
    entities: TechnicalEntities = field(default_factory=TechnicalEntities)


def is_internal_ip(ip: str) -> bool:
    try:
        addr = ipaddress.ip_address(ip)
    except ValueError:
        return False
    return any(addr in n for n in _INTERNAL_NETS)


def _regex_spans(text: str) -> list[Span]:
    spans: list[Span] = []
    for m in _EMAIL.finditer(text):
        spans.append(Span(m.start(), m.end(), "EMAIL_ADDRESS", 1.0))
    for m in _PHONE_FR.finditer(text):
        spans.append(Span(m.start(), m.end(), "PHONE_NUMBER", 0.95))
    for m in _IPV4.finditer(text):
        try:
            ipaddress.ip_address(m.group())
        except ValueError:
            continue
        kind = "INTERNAL_IP" if is_internal_ip(m.group()) else "EXTERNAL_IP"
        spans.append(Span(m.start(), m.end(), kind, 1.0))
    for m in _HOST.finditer(text):
        spans.append(Span(m.start(), m.end(), "HOSTNAME", 0.99))
    for rx in _USER:
        for m in rx.finditer(text):
            g = 1 if rx.groups else 0
            spans.append(Span(m.start(g), m.end(g), "USERNAME", 0.98))
    for m in _CTX_USER.finditer(text):
        cand = m.group(1)
        looks_like_id = any(c.isdigit() or c in "._-" for c in cand)
        if cand.casefold() in _COMMON or not (cand.islower() or looks_like_id):
            continue
        spans.append(Span(m.start(1), m.end(1), "USERNAME", 0.9))
    return spans


_OPEN, _CLOSE = "([{«\"'<", ")]}»\"'>"
_EDGE = " \t\n,;:.!?"


def _trim(text: str, s: Span) -> Span:
    """Retire la ponctuation de bord d'un span sans casser les parenthèses équilibrées :
    « (06 12 34 56 78 » -> « 06 12 34 56 78 », mais « (555) 123-4567 » reste entier."""
    start, end = s.start, s.end
    while start < end:
        value = text[start:end]
        if value[0] in _EDGE:
            start += 1
        elif value[-1] in _EDGE and s.kind != "EMAIL_ADDRESS":
            end -= 1
        elif value[0] in _OPEN and _CLOSE[_OPEN.index(value[0])] not in value[1:]:
            start += 1
        elif value[-1] in _CLOSE and _OPEN[_CLOSE.index(value[-1])] not in value[:-1]:
            end -= 1
        else:
            break
    return Span(start, end, s.kind, s.score)


@lru_cache(maxsize=1)
def _analyzer():
    from presidio_analyzer import AnalyzerEngine
    from presidio_analyzer.nlp_engine import NlpEngineProvider

    ignore = ["MISC", "ORG", "LOC", "GPE", "NORP", "FAC", "PRODUCT", "WORK_OF_ART", "EVENT",
              "LAW", "LANGUAGE", "DATE", "TIME", "PERCENT", "MONEY", "QUANTITY", "ORDINAL", "CARDINAL"]
    conf = {"nlp_engine_name": "spacy",
            "models": [{"lang_code": "fr", "model_name": settings.spacy_model_fr},
                       {"lang_code": "en", "model_name": settings.spacy_model_en}],
            "ner_model_configuration": {"labels_to_ignore": ignore}}
    nlp = NlpEngineProvider(nlp_configuration=conf).create_engine()
    return AnalyzerEngine(nlp_engine=nlp, supported_languages=["fr", "en"])


# Le NER prend parfois des noms de produits ou d'outils pour des personnes.
_NOT_PERSON = {w.casefold() for w in (
    "alerte alert wazuh suricata mitre att&ck outlook teams windows microsoft onedrive excel word "
    "forticlient papercut exemplia vpn mfa authenticator sharepoint office erp sshd nmap powershell "
    "bonjour hello merci cordialement").split()}


def _presidio_spans(text: str, language: Lang) -> list[Span]:
    results = _analyzer().analyze(text, language=language,
                                  entities=["PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER"],
                                  score_threshold=0.35)
    spans = []
    for r in results:
        words = {w.casefold().strip(".,:;!?()") for w in text[r.start:r.end].split()}
        if r.entity_type == "PERSON" and words & _NOT_PERSON:
            continue
        spans.append(Span(r.start, r.end, r.entity_type, r.score))
    return spans


def _resolve_overlaps(spans: list[Span]) -> list[Span]:
    """Garde les spans sans chevauchement : le plus long d'abord, puis le plus sûr."""
    chosen: list[Span] = []
    for s in sorted(spans, key=lambda s: (-(s.end - s.start), -s.score, s.start)):
        if s.end <= s.start:
            continue
        if all(s.end <= c.start or s.start >= c.end for c in chosen):
            chosen.append(s)
    return sorted(chosen, key=lambda s: s.start)


class Masker:
    """Remplace les entités par des pseudonymes stables au sein d'un même ticket."""

    def __init__(self, use_ner: bool = True) -> None:
        self.use_ner = use_ner

    def mask(self, text: str, language: Lang = "fr", mapping: dict[str, str] | None = None,
             known: list[tuple[str, str]] = ()) -> MaskResult:
        """`known` : couples (valeur, type) issus de champs structurés (alertes SIEM),
        masqués partout où la valeur apparaît, même si aucune regex ne la reconnaît."""
        mapping = dict(mapping or {})
        reverse = {v.casefold(): k for k, v in mapping.items()}
        counters: dict[str, int] = {}
        for ph in mapping:
            m = PLACEHOLDER_RE.fullmatch(ph)
            if m:
                counters[m.group(1)] = max(counters.get(m.group(1), 0), int(m.group(2)))

        spans = _regex_spans(text)
        for value, kind in known:
            if value:
                spans += [Span(m.start(), m.end(), kind, 1.0)
                          for m in re.finditer(rf"(?<![\w.-]){re.escape(value)}(?![\w-])", text)]
        if self.use_ner:
            spans += _presidio_spans(text, language)
        spans = [_trim(text, sp) for sp in spans]
        out, cursor = [], 0
        for s in _resolve_overlaps(spans):
            value = text[s.start:s.end]
            key = value.casefold()
            if key not in reverse:
                prefix = PREFIX[s.kind]
                counters[prefix] = counters.get(prefix, 0) + 1
                ph = f"<{prefix}_{counters[prefix]}>"
                mapping[ph], reverse[key] = value, ph
            out.append(text[cursor:s.start])
            out.append(reverse[key])
            cursor = s.end
        out.append(text[cursor:])
        return MaskResult(text="".join(out), mapping=mapping, entities=entities_from(mapping))


def entities_from(mapping: dict[str, str]) -> TechnicalEntities:
    def values(prefix: str) -> list[str]:
        return [v for k, v in mapping.items() if k.startswith(f"<{prefix}_")]
    return TechnicalEntities(external_ips=values("IP_EXT"), hostnames=values("HOTE"),
                             usernames=values("COMPTE"))


def unmask(text: str, mapping: dict[str, str]) -> str:
    return PLACEHOLDER_RE.sub(lambda m: mapping.get(m.group(0), m.group(0)), text)


def resolve_action_param(value: str, mapping: dict[str, str]) -> str | None:
    """Résout un pseudonyme proposé par le LLM en valeur réelle, si c'est un identifiant
    technique d'action (IP externe, poste, compte). Toute autre valeur est rejetée :
    le LLM ne peut pas inventer une cible ni viser une donnée personnelle."""
    m = PLACEHOLDER_RE.fullmatch(value.strip())
    if not m or m.group(1) not in ACTIONABLE_PREFIXES:
        return None
    return mapping.get(m.group(0))


@lru_cache(maxsize=1)
def get_masker() -> Masker:
    return Masker()

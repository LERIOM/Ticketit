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
    "FORGED": "TEXTE",          # un « pseudonyme » écrit dans le ticket lui-même
}
# Pseudonymes que le code accepte de résoudre en paramètre d'action.
ACTIONABLE_PREFIXES = ("IP_EXT", "HOTE", "COMPTE")
PLACEHOLDER_RE = re.compile(r"<(" + "|".join(PREFIX.values()) + r")_(\d+)>")
# Ordre de priorité quand deux détections se chevauchent : les règles déterministes
# l'emportent sur le NER (« Server 8.8.8.8 » ne doit pas devenir une personne).
_PRIORITY = {"FORGED": 0, "EMAIL_ADDRESS": 1, "INTERNAL_IP": 1, "EXTERNAL_IP": 1, "HOSTNAME": 1,
             "USERNAME": 2, "PHONE_NUMBER": 2, "PERSON": 3}

_INTERNAL_NETS = [ipaddress.ip_network(n) for n in (
    "10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16", "127.0.0.0/8",
    "169.254.0.0/16", "0.0.0.0/8", "100.64.0.0/10", "::1/128", "fc00::/7", "fe80::/10")]

_FORGED = re.compile(r"<\s*[A-Za-z][A-Za-z_]{1,20}_\d+\s*>")
_IPV4 = re.compile(r"(?<!\d)(?<!\d\.)(?:\d{1,3}\.){3}\d{1,3}(?!\d|\.\d)")
# Un numéro de version (« Office 16.0.1.5 », « build 1.2.3.4 ») n'est pas une IP.
_VERSION_BEFORE = re.compile(r"(?i)\b(?:version|ver\.?|v|build|release|firmware|office|kb)\s*:?\s*$")
_IPV6 = re.compile(r"(?i)(?<![\w:])(?:[0-9a-f]{0,4}:){2,7}[0-9a-f]{0,4}(?![\w:])")
# Postes et serveurs : convention Exemplia (SRV-WEB-01) et noms Windows courants
# (DESKTOP-AB12CD3, WIN-7K3L9QX, LAPTOP-…, DC01), plus les FQDN internes.
_HOST_PREFIX = r"(?:SRV|PC|DC|LT|WS|FW|NAS|SW|RTR|VM|DESKTOP|LAPTOP|WIN|NB|MAC|HOST)"
_HOST = re.compile(rf"(?i)\b{_HOST_PREFIX}(?:-[A-Z0-9]+)+\b|\b(?:SRV|PC|DC|NAS|VM|FW|RTR|HOST)\d{{2,}}[A-Z0-9]*\b")
_FQDN = re.compile(r"(?i)\b[a-z0-9][a-z0-9-]*(?:\.[a-z0-9-]+)*\.(?:corp|lan|local|internal|intra)(?:\.[a-z0-9-]+)*\b")
_PHONE_FR = re.compile(r"(?<!\d)(?:\+33\s?|0)[1-9](?:[\s.-]?\d{2}){4}(?!\d)")
_EMAIL = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
_ID = r"([A-Za-z][\w.-]{1,30}[A-Za-z0-9])(?![\w@-]|\.\w)"
_USER = [
    re.compile(r"(?<![\w.@-])[a-z]\.[a-z]{2,}(?:-[a-z]+)?(?![\w@-]|\.[a-z])"),     # j.martin
    re.compile(r"\bsvc-[a-z0-9-]+\b"),                                            # comptes de service
    re.compile(r"(?i)\b(?:compte|account|utilisateur|user|login|identifiant)\s+(?:de\s+l'|de\s+|d')?"
               r"[«\"']?\s*(admin|administrateur|administrator|root|guest|invit[ée])\b"),
]
# Contextes forts : ce qui suit est forcément un identifiant de compte.
_USER_STRONG = [
    re.compile(r"\b[A-Z][A-Z0-9-]{1,15}\\" + _ID),                                  # CORP\jsmith
    re.compile(r"(?i)\b(?:logged|signed)\s+(?:in|on)\s+as\s+" + _ID),               # logged in as tnguyen
    re.compile(r"(?i)\bconnecté\s+en\s+tant\s+que\s+" + _ID),
    re.compile(r"(?i)\b(?:reset|unlock|re-?enable|disable)\s+(?:the\s+)?(?:password|mfa|2fa|account|login)s?"
               r"\s*(?:for|of|:)\s*(?:user\s+)?" + _ID),                            # reset MFA for mjones
    re.compile(r"\buid=\d+\(" + _ID[:-len(r"(?![\w@-]|\.\w)")] + r"\)"),             # uid=1001(jsmith)
]
_USER_EXPLICIT = {4}            # uid=… : toujours un compte, même si c'est un mot du dictionnaire
# Identifiant après un mot-clé de compte (« user jsmith », « username: mlopez2 »).
_CTX_USER = re.compile(
    r"(?i)\b(?:user(?:name)?|user\s*id|account|login|logon|uid|compte|utilisateur|identifiant)\b"
    r"\s*(?:(?P<sep>[:=]|\bnamed\b|\bnommé\b)|\b(?:is|est|for|of|pour|de|du)\b)?\s*[«\"'`]?\s*"
    r"(?P<id>[A-Za-z][A-Za-z0-9._-]{1,30}[A-Za-z0-9])(?![\w@-]|\.\w)")
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
_COMMON |= set("""doesn isn wasn don didn won aren hasn haven couldn shouldn wouldn everyone everybody
anyone someone nobody employees staff finance expected""".split())
_PRIVILEGED = {"admin", "administrator", "administrateur", "root", "guest", "svc-backup"}


@lru_cache(maxsize=1)
def _dictionary() -> frozenset[str]:
    """Mots anglais et français connus (tables de lemmes de spaCy, ~170 000 entrées)."""
    words: set[str] = set()
    for nlp in _analyzer().nlp_engine.nlp.values():
        lem = nlp.get_pipe("lemmatizer")
        if "lemma_index" in lem.lookups.tables:
            idx = lem.lookups.get_table("lemma_index")
            for pos in idx.keys():
                words |= set(idx[pos])
    return frozenset(words)


def _is_word(cand: str) -> bool:
    c = cand.lower()
    forms = {c, c[:-1] if c.endswith("s") else c, c[:-2] if c.endswith(("es", "ed")) else c,
             c[:-3] + "y" if c.endswith("ies") else c, c[:-1] if c.endswith("ed") else c,
             c[:-3] if c.endswith("ing") else c, c[:-3] + "e" if c.endswith("ing") else c}
    return bool(forms & _dictionary())


def _accept_user(cand: str, explicit: bool = False) -> bool:
    """Un identifiant de compte : jsmith, mlopez2, j_doe… mais pas « down » ni « Emily »."""
    low = cand.casefold()
    if low in _PRIVILEGED:
        return True
    if low in _COMMON:
        return False
    if any(c.isdigit() or c in "._-" for c in cand):
        return True
    if not cand.islower():
        return False
    return explicit or not _is_word(cand)


# Formule de politesse suivie d'un prénom en fin de ligne : « Thanks,\nMike », « Cheers, Tom ».
_SIGNATURE = re.compile(
    r"(?im)^[ \t]{0,20}(?:thanks(?:\s+(?:a\s+lot|again|so\s+much))?|thank\s+you|many\s+thanks|"
    r"(?:best|kind|warm)\s+regards|regards|best|cheers|sincerely|merci(?:\s+(?:beaucoup|d'avance))?|"
    r"cordialement|bien\s+à\s+vous|bonne\s+journée)[ \t]{0,20}[,!.]?[ \t]{0,20}(?:\n[ \t]{0,20})?"
    r"(?:[-–—][ \t]{0,5})?([A-ZÀ-Þ][a-zà-ÿ'’-]+(?:[ \t]{1,5}[A-ZÀ-Þ][a-zà-ÿ'’.-]+){0,2})[ \t]{0,20}$")
_DEPARTMENTS = set("accounting finance hr department security operations sales marketing legal procurement "
                   "it team support office management desk helpdesk service services group".split())


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


def _parse_ipv4(value: str) -> ipaddress.IPv4Address | None:
    """Accepte aussi les zéros en tête (192.168.001.005), que `ipaddress` refuse."""
    parts = value.split(".")
    if len(parts) != 4 or not all(p.isdigit() and int(p) <= 255 for p in parts):
        return None
    return ipaddress.IPv4Address(".".join(str(int(p)) for p in parts))


def is_internal_ip(ip: str) -> bool:
    try:
        addr = ipaddress.ip_address(ip)
    except ValueError:
        addr = _parse_ipv4(ip)
        if addr is None:
            return False
    return any(addr in n for n in _INTERNAL_NETS)


def _is_netmask(addr: ipaddress.IPv4Address) -> bool:
    bits = format(int(addr), "032b")
    return addr.packed[0] == 255 and "01" not in bits


def _regex_spans(text: str) -> list[Span]:
    spans: list[Span] = [Span(m.start(), m.end(), "FORGED", 1.0) for m in _FORGED.finditer(text)]
    for m in _EMAIL.finditer(text):
        spans.append(Span(m.start(), m.end(), "EMAIL_ADDRESS", 1.0))
    for m in _PHONE_FR.finditer(text):
        spans.append(Span(m.start(), m.end(), "PHONE_NUMBER", 0.95))
    for m in _IPV4.finditer(text):
        addr = _parse_ipv4(m.group())
        if addr is None or _is_netmask(addr):
            continue
        kind = "INTERNAL_IP" if is_internal_ip(m.group()) else "EXTERNAL_IP"
        if kind == "EXTERNAL_IP" and _VERSION_BEFORE.search(text[max(0, m.start() - 20):m.start()]):
            continue
        spans.append(Span(m.start(), m.end(), kind, 1.0))
    for m in _HOST.finditer(text):
        name = m.group()
        if name.isupper() or any(c.isdigit() for c in name):   # « Mac-Address », « NB-IoT » ne sont pas des postes
            spans.append(Span(m.start(), m.end(), "HOSTNAME", 0.99))
    for m in _FQDN.finditer(text):
        labels = m.group().split(".")
        if len(labels) >= 3 or any(c.isdigit() or c == "-" for c in labels[0]):   # pas « wiki.local »
            spans.append(Span(m.start(), m.end(), "HOSTNAME", 0.99))
    for rx in _USER:
        for m in rx.finditer(text):
            g = 1 if rx.groups else 0
            spans.append(Span(m.start(g), m.end(g), "USERNAME", 0.98))
    for i, rx in enumerate(_USER_STRONG):
        for m in rx.finditer(text):
            if _accept_user(m.group(1), explicit=i in _USER_EXPLICIT):
                spans.append(Span(m.start(1), m.end(1), "USERNAME", 0.95))
    for m in _CTX_USER.finditer(text):
        if _accept_user(m.group("id"), explicit=bool(m.group("sep"))):
            spans.append(Span(m.start("id"), m.end("id"), "USERNAME", 0.9))
    for m in _SIGNATURE.finditer(text):
        if not set(m.group(1).casefold().replace("-", " ").split()) & (_NOT_PERSON | _DEPARTMENTS):
            spans.append(Span(m.start(1), m.end(1), "PERSON", 0.9))
    for m in _IPV6.finditer(text):
        try:
            addr = ipaddress.IPv6Address(m.group())
        except ValueError:
            continue
        kind = "INTERNAL_IP" if any(addr in n for n in _INTERNAL_NETS if n.version == 6) else "EXTERNAL_IP"
        spans.append(Span(m.start(), m.end(), kind, 1.0))
    return spans


_OPEN, _CLOSE = "([{«\"'<", ")]}»\"'>"
_EDGE = " \t\n,;:.!?"


def _trim(text: str, s: Span) -> Span:
    """Retire la ponctuation de bord d'un span sans casser les parenthèses équilibrées :
    « (06 12 34 56 78 » -> « 06 12 34 56 78 », mais « (555) 123-4567 » reste entier."""
    if s.kind == "FORGED":
        return s
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


# Le NER prend parfois des noms de produits, d'outils ou des mots d'en-tête pour des personnes.
_NOT_PERSON = {w.casefold() for w in (
    "alerte alert wazuh suricata mitre att&ck outlook teams windows microsoft onedrive excel word "
    "forticlient papercut exemplia vpn mfa authenticator sharepoint office erp sshd nmap powershell "
    "bonjour hello merci cordialement de from tel email e-mail mail server serveur support team "
    "service desk helpdesk it admin ula snapshot "
    "adobe acrobat reader docker jira confluence salesforce jenkins cisco anyconnect safari chrome "
    "firefox edge zoom slack zapier clickup mongodb macos monterey ventura sonoma ubuntu linux "
    "android ios iphone ipad citrix vmware okta aws azure gcp kubernetes github gitlab dropbox "
    "google gmail workspace notion trello asana hubspot shopify quickbooks sap oracle postgresql "
    "mysql redis nginx apache tomcat kafka tableau powerbi git").split()}


_PARTICLES = {"de", "da", "di", "del", "della", "du", "des", "la", "le", "van", "von", "der", "den",
              "bin", "ben", "al", "el", "y", "e"}


def _looks_like_name(value: str) -> bool:
    raw = [w.strip(".,:;!?()'’") for w in value.replace("-", " ").split()]
    raw = [w for w in raw if w]
    words = {w.casefold() for w in raw}
    if not raw or any(c.isdigit() or c in "\\/@:=<>_" for c in value) or words <= _NOT_PERSON:
        return False
    acronyms = [w for w in raw if w.isupper() and 2 <= len(w) <= 4]   # sigles : « CI », « EMR », « SE Mouse »
    if acronyms and (len(raw) == 1 or not all(w.isupper() for w in raw)):   # mais « JOHN SMITH », « S. Williams »
        return False
    capitalised = any(w[0].isupper() for w in raw)
    if capitalised and any(w.islower() and w not in _PARTICLES for w in raw):   # « Razer keyboards »
        return False
    return len(value.strip()) >= 2


_ID_LIKE = re.compile(r"[a-z][a-z0-9._-]{2,30}")


def _presidio_spans(text: str, language: Lang) -> list[Span]:
    results = _analyzer().analyze(text, language=language,
                                  entities=["PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER"],
                                  score_threshold=0.35)
    keep = []
    for r in results:
        value = text[r.start:r.end]
        if r.entity_type == "PERSON" and not _looks_like_name(value):
            if _ID_LIKE.fullmatch(value) and any(c.isdigit() for c in value):     # « jdoe42 »
                keep.append(Span(r.start, r.end, "USERNAME", r.score))
            continue
        if r.entity_type == "PHONE_NUMBER" and _IPV4.fullmatch(value.strip()):   # 255.255.255.0
            continue
        keep.append(Span(r.start, r.end, r.entity_type, r.score))
    return keep


def _resolve_overlaps(text: str, spans: list[Span]) -> list[Span]:
    """Garde les spans sans chevauchement : le type le plus fiable d'abord, puis le plus
    long. Un nom (NER) qui chevauche une détection sûre est réduit à sa partie libre."""
    chosen: list[Span] = []
    for s in sorted(spans, key=lambda s: (_PRIORITY[s.kind], -(s.end - s.start), -s.score, s.start)):
        if s.end <= s.start:
            continue
        clashes = [c for c in chosen if not (s.end <= c.start or s.start >= c.end)]
        if not clashes:
            chosen.append(s)
        elif s.kind == "PERSON":
            gaps, pos = [], s.start
            for c in sorted(clashes, key=lambda c: c.start):
                if c.start > pos:
                    gaps.append((pos, min(c.start, s.end)))
                pos = max(pos, c.end)
            if pos < s.end:
                gaps.append((pos, s.end))
            for a, b in gaps:
                rest = _trim(text, Span(a, b, "PERSON", s.score))
                if rest.end > rest.start and _looks_like_name(text[rest.start:rest.end]):
                    chosen.append(rest)
    return sorted(chosen, key=lambda s: s.start)


class Masker:
    """Remplace les entités par des pseudonymes stables au sein d'un même ticket."""

    def __init__(self, use_ner: bool = True) -> None:
        self.use_ner = use_ner

    def mask(self, text: str, language: Lang = "fr", mapping: dict[str, str] | None = None,
             known: list[tuple[str, str]] = ()) -> MaskResult:
        """`known` : couples (valeur, type) issus de champs structurés (alertes SIEM, demandeur),
        masqués partout où la valeur apparaît (sans tenir compte de la casse)."""
        mapping = dict(mapping or {})
        counters: dict[str, int] = {}
        reverse: dict[tuple[str, str], str] = {}
        for ph, value in mapping.items():
            m = PLACEHOLDER_RE.fullmatch(ph)
            if m:
                counters[m.group(1)] = max(counters.get(m.group(1), 0), int(m.group(2)))
                reverse[(m.group(1), value)] = ph

        spans = _regex_spans(text)
        for value, kind in known:
            if kind not in PREFIX or kind == "FORGED":
                raise ValueError(f"type d'entité inconnu : {kind!r}")
            if value:
                flags = 0 if kind == "PERSON" else re.IGNORECASE
                spans += [Span(m.start(), m.end(), kind, 1.0) for m in
                          re.finditer(rf"(?<![\w.-]){re.escape(value)}(?![\w-])", text, flags)]
        if self.use_ner:
            spans += _presidio_spans(text, language)
        spans = [_trim(text, sp) for sp in spans]
        # Une valeur repérée une fois (« logged in as tnguyen ») est masquée partout.
        for sp in _resolve_overlaps(text, spans):
            if sp.kind != "FORGED":
                value = text[sp.start:sp.end]
                spans += [Span(m.start(), m.end(), sp.kind, sp.score * 0.99) for m in
                          re.finditer(rf"(?<![\w.@-]){re.escape(value)}(?![\w@-])", text)]
        out, cursor = [], 0
        for s in _resolve_overlaps(text, spans):
            value, prefix = text[s.start:s.end], PREFIX[s.kind]
            if (prefix, value) not in reverse:
                counters[prefix] = counters.get(prefix, 0) + 1
                ph = f"<{prefix}_{counters[prefix]}>"
                mapping[ph] = value
                reverse[(prefix, value)] = ph
            out.append(text[cursor:s.start])
            out.append(reverse[(prefix, value)])
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

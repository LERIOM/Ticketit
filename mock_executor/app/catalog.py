"""Catalogue des outils et version simplifiée du tableau des niveaux (contrat v1).

Ce n'est PAS le moteur d'autorisation de Florent : juste assez de logique pour
que l'engine reçoive des réponses réalistes pour chaque status.
"""
import ipaddress
import os
from typing import Any

L1_THRESHOLD = float(os.environ.get("MOCK_L1_THRESHOLD", "0.80"))
PROTECTED_IPS = {"203.0.113.250"}
PROTECTED_ACCOUNTS = {"admin", "svc-backup"}
PROTECTED_HOSTS = {"DC-01"}

_USERNAME = {"type": "string", "minLength": 1, "maxLength": 64}
_HOSTNAME = {"type": "string", "minLength": 1, "maxLength": 64}

TOOLS: list[dict[str, Any]] = [
    {"name": "logs_search", "level": 0, "reversible": False,
     "description": "Cherche dans les logs du labo (format proche Wazuh/Suricata)",
     "params_schema": {"type": "object",
                       "properties": {"query": {"type": "string", "minLength": 1, "maxLength": 256},
                                      "since_minutes": {"type": "integer", "minimum": 1, "maximum": 1440}},
                       "required": ["query", "since_minutes"]}},
    {"name": "account_info", "level": 0, "reversible": False,
     "description": "Consulte l'état d'un compte de l'annuaire",
     "params_schema": {"type": "object", "properties": {"username": _USERNAME},
                       "required": ["username"]}},
    {"name": "block_ip", "level": 1, "reversible": True,
     "description": "Bloque une IP externe sur le pare-feu pour une durée limitée",
     "params_schema": {"type": "object",
                       "properties": {"ip": {"type": "string"},
                                      "duration_hours": {"type": "integer", "minimum": 1, "maximum": 24}},
                       "required": ["ip", "duration_hours"]}},
    {"name": "force_password_reset", "level": 1, "reversible": True,
     "description": "Force le changement de mot de passe à la prochaine connexion",
     "params_schema": {"type": "object", "properties": {"username": _USERNAME},
                       "required": ["username"]}},
    {"name": "isolate_host", "level": 2, "reversible": True,
     "description": "Isole un poste du réseau via l'EDR",
     "params_schema": {"type": "object", "properties": {"hostname": _HOSTNAME},
                       "required": ["hostname"]}},
    {"name": "disable_account", "level": 2, "reversible": True,
     "description": "Désactive un compte de l'annuaire",
     "params_schema": {"type": "object", "properties": {"username": _USERNAME},
                       "required": ["username"]}},
]
TOOLS_BY_NAME = {t["name"]: t for t in TOOLS}

_PY_TYPES = {"string": str, "integer": int}


def validate_params(tool: dict[str, Any], params: dict[str, Any]) -> str | None:
    """Renvoie la raison du refus, ou None si les paramètres sont valides."""
    schema = tool["params_schema"]
    props = schema["properties"]
    missing = [k for k in schema["required"] if k not in params]
    if missing:
        return f"paramètres manquants : {', '.join(missing)}"
    extra = sorted(set(params) - set(props))
    if extra:
        return f"paramètres inattendus : {', '.join(extra)}"
    for key, rule in props.items():
        value = params[key]
        expected = _PY_TYPES[rule["type"]]
        if not isinstance(value, expected) or isinstance(value, bool):
            return f"{key} doit être de type {rule['type']}"
        if "minimum" in rule and value < rule["minimum"]:
            return f"{key} < {rule['minimum']}"
        if "maximum" in rule and value > rule["maximum"]:
            return f"{key} > {rule['maximum']}"
        if "minLength" in rule and len(value) < rule["minLength"]:
            return f"{key} trop court"
        if "maxLength" in rule and len(value) > rule["maxLength"]:
            return f"{key} trop long"
    if "ip" in params:
        try:
            ipaddress.ip_address(params["ip"])
        except ValueError:
            return f"ip invalide : {params['ip']!r} (une seule adresse, pas de plage)"
    for key in ("username", "hostname"):
        if key in params and not params[key].replace("-", "").replace(".", "").replace("_", "").isalnum():
            return f"{key} contient des caractères interdits"
    return None


# Liste explicite : ipaddress.is_private/is_global classent aussi les plages de
# documentation (203.0.113.0/24, 198.51.100.0/24) comme privées, or ce sont les
# IP « publiques » du jeu d'intégration commun.
_NEVER_AUTO_BLOCK = [ipaddress.ip_network(n) for n in (
    "10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16",   # RFC 1918
    "127.0.0.0/8", "::1/128",                          # bouclage
    "0.0.0.0/8", "169.254.0.0/16", "224.0.0.0/4", "255.255.255.255/32",
    "fc00::/7", "fe80::/10",
)]


def ip_auto_blockable(ip: str) -> bool:
    addr = ipaddress.ip_address(ip)
    if any(addr.version == n.version and addr in n for n in _NEVER_AUTO_BLOCK):
        return False
    return ip not in PROTECTED_IPS

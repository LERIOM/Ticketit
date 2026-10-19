"""État en mémoire du faux labo : pare-feu, annuaire, EDR, logs, audit, idempotence.

Les données reprennent le jeu d'intégration commun (ssh_bruteforce, port_scan,
phishing_report, cas piège). `STATE.reset()` remet tout à l'état initial.
"""
import json
import threading
from collections import Counter
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

from . import catalog


class TargetNotFound(Exception):
    """La cible n'existe pas dans le labo : l'action finit en `failed`."""


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.isoformat().replace("+00:00", "Z")


def _seed_logs(now: datetime) -> list[dict[str, Any]]:
    logs = []
    for i in range(12):  # ssh_bruteforce : 12 échecs en 2 minutes
        logs.append({"timestamp": _iso(now - timedelta(minutes=12, seconds=-10 * i)),
                     "source": "wazuh", "rule": {"id": "5710", "level": 10,
                                                 "description": "sshd: authentication failed"},
                     "agent": {"name": "SRV-WEB-01"}, "data": {"srcip": "203.0.113.5", "dstuser": "root"}})
    logs.append({"timestamp": _iso(now - timedelta(minutes=30)), "source": "suricata",
                 "event_type": "alert", "src_ip": "198.51.100.23", "dest_host": "SRV-WEB-01",
                 "alert": {"signature": "ET SCAN Possible Nmap scan - 300 ports in 30s", "severity": 2}})
    logs.append({"timestamp": _iso(now - timedelta(minutes=45)), "source": "proxy",
                 "user": "j.martin", "host": "PC-COMPTA-07",
                 "url": "http://micr0soft-login.example/auth", "action": "POST credentials"})
    return logs


class MockState:
    def __init__(self) -> None:
        self.lock = threading.RLock()
        self.reset()

    def reset(self) -> None:
        with self.lock:
            self.audit: list[dict[str, Any]] = []            # ajout seul
            self.responses: dict[str, dict[str, Any]] = {}   # idempotence par request_id
            self.decided: set[str] = set()                   # audit_id en attente déjà traités
            self.undone: set[str] = set()                    # audit_id déjà annulés
            self.runs: Counter[str] = Counter()              # exécutions réelles par request_id
            self.blocked_ips: dict[str, str] = {}
            self.accounts = {u: {"active": True, "must_change_password": False}
                             for u in ("j.martin", "a.durand", "admin", "svc-backup")}
            self.hosts = {h: {"isolated": False} for h in ("SRV-WEB-01", "PC-COMPTA-07", "DC-01")}
            self.logs = _seed_logs(_now())
            self._counter = 0

    # ------------------------------------------------------------- audit
    def append_audit(self, **fields: Any) -> dict[str, Any]:
        self._counter += 1
        entry = {"audit_id": f"A-{self._counter:06d}", "timestamp": _iso(_now()),
                 "approver": None, "undo_of": None, **fields}
        self.audit.append(entry)
        return entry

    def find_audit(self, audit_id: str) -> dict[str, Any] | None:
        return next((e for e in self.audit if e["audit_id"] == audit_id), None)

    # ------------------------------------------------------------- outils
    def run(self, request_id: str, tool: str, params: dict[str, Any]) -> dict[str, Any]:
        self.runs[request_id] += 1
        if tool == "logs_search":
            since = _now() - timedelta(minutes=params["since_minutes"])
            q = params["query"].lower()
            hits = [log for log in self.logs
                    if datetime.fromisoformat(log["timestamp"].replace("Z", "+00:00")) >= since
                    and q in json.dumps(log).lower()]
            return {"count": len(hits), "hits": hits[:50]}
        if tool == "account_info":
            acc = self._account(params["username"])
            return {"username": params["username"], **acc,
                    "protected": params["username"] in catalog.PROTECTED_ACCOUNTS}
        if tool == "block_ip":
            until = _iso(_now() + timedelta(hours=params["duration_hours"]))
            self.blocked_ips[params["ip"]] = until
            return {"ip": params["ip"], "blocked_until": until}
        if tool == "force_password_reset":
            self._account(params["username"])["must_change_password"] = True
            return {"username": params["username"], "must_change_password": True}
        if tool == "isolate_host":
            self._host(params["hostname"])["isolated"] = True
            return {"hostname": params["hostname"], "isolated": True}
        if tool == "disable_account":
            self._account(params["username"])["active"] = False
            return {"username": params["username"], "active": False}
        raise ValueError(f"outil sans implémentation : {tool}")

    def undo(self, tool: str, params: dict[str, Any]) -> dict[str, Any]:
        if tool == "block_ip":
            self.blocked_ips.pop(params["ip"], None)
            return {"ip": params["ip"], "blocked_until": None}
        if tool == "force_password_reset":
            self._account(params["username"])["must_change_password"] = False
            return {"username": params["username"], "must_change_password": False}
        if tool == "isolate_host":
            self._host(params["hostname"])["isolated"] = False
            return {"hostname": params["hostname"], "isolated": False}
        if tool == "disable_account":
            self._account(params["username"])["active"] = True
            return {"username": params["username"], "active": True}
        raise ValueError(f"outil non réversible : {tool}")

    def _account(self, username: str) -> dict[str, Any]:
        if username not in self.accounts:
            raise TargetNotFound(f"compte inconnu dans l'annuaire : {username}")
        return self.accounts[username]

    def _host(self, hostname: str) -> dict[str, Any]:
        if hostname not in self.hosts:
            raise TargetNotFound(f"poste inconnu de l'EDR : {hostname}")
        return self.hosts[hostname]


def new_request_id() -> str:
    return str(uuid4())


STATE = MockState()

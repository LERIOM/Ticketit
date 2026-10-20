"""SEUL point d'accès au module d'exécution de Florent (contrat v1).

Règles :
- délai global de `executor_timeout_s` (5 s) par tentative, lecture du corps comprise
  (pire cas ≈ 2 s de connexion + 5 s, jamais plus) ;
- `/v1/execute` et les lectures : une seule nouvelle tentative, avec le MÊME
  request_id (l'executor est idempotent), si pas de réponse, réponse illisible ou 5xx ;
- approbations et annulations : jamais rejouées automatiquement ;
- toute erreur lève `ExecutorError` : l'appelant escalade le ticket, il n'y a
  jamais d'action « par défaut ».
"""
import json
import re
import time
from typing import Any
from urllib.parse import quote

import httpx
from pydantic import TypeAdapter, ValidationError

from .config import settings
from .models import (
    ApprovalRequest, AuditEntry, ExecuteRequest, ExecuteResponse, HealthResponse, ToolSpec,
)


class ExecutorError(Exception):
    """Échec d'un appel à l'executor : le ticket doit être escaladé."""


class ExecutorUnavailable(ExecutorError):
    """Pas de réponse exploitable après la nouvelle tentative (délai, réseau, 5xx)."""


class ExecutorProtocolError(ExecutorError):
    """Réponse contraire au contrat v1 (401, 422, corps invalide…)."""


class InvalidRequest(ExecutorError):
    """Demande refusée avant tout appel (ex. audit_id piégé)."""


_TOOLS = TypeAdapter(list[ToolSpec])
_AUDIT = TypeAdapter(list[AuditEntry])
# Un audit_id est mis dans l'URL : ni « / », ni « . », ni « ? »… (sinon x/../../undo/A-1
# transformerait une validation en annulation).
_AUDIT_ID = re.compile(r"[A-Za-z0-9_-]{1,64}")


def _base_url(url: str) -> str:
    """Accepte `http://executor:8100` comme `http://executor:8100/v1` (servers.url du contrat)."""
    url = url.rstrip("/")
    return url[:-3] if url.endswith("/v1") else url


class ExecutorClient:
    def __init__(self, base_url: str | None = None, api_key: str | None = None,
                 timeout_s: float | None = None, http: httpx.Client | None = None) -> None:
        self.timeout_s = settings.executor_timeout_s if timeout_s is None else timeout_s
        self._headers = {"X-API-Key": settings.executor_api_key if api_key is None else api_key}
        self._http = http or httpx.Client(
            base_url=_base_url(base_url or settings.executor_url),
            timeout=httpx.Timeout(self.timeout_s, connect=min(2.0, self.timeout_s)))

    # ------------------------------------------------------------ transport
    def _attempt(self, method: str, path: str, **kw: Any) -> tuple[int, bytes]:
        """Une tentative, bornée par un délai global (un serveur qui envoie la réponse
        octet par octet ne peut pas retenir l'appel au-delà du délai)."""
        deadline = time.monotonic() + self.timeout_s
        with self._http.stream(method, f"/v1{path}", headers=self._headers, **kw) as r:
            body = bytearray()
            for chunk in r.iter_bytes():
                body += chunk
                if time.monotonic() > deadline:
                    raise httpx.ReadTimeout("délai global dépassé")
            if time.monotonic() > deadline:
                raise httpx.ReadTimeout("délai global dépassé")
            return r.status_code, bytes(body)

    def _call(self, method: str, path: str, *, retry: bool, **kw: Any) -> Any:
        attempts = 2 if retry else 1
        last = "aucune tentative"
        for _ in range(attempts):
            try:
                status, body = self._attempt(method, path, **kw)
            except httpx.TimeoutException:
                last = f"délai de {self.timeout_s:g} s dépassé"
                continue
            except httpx.RequestError as exc:          # réseau, corps illisible…
                last = f"executor injoignable ou réponse illisible ({exc.__class__.__name__})"
                continue
            if status >= 500:
                last = f"erreur serveur {status}"
                continue
            if status == 401:
                raise ExecutorProtocolError("clé API refusée par l'executor (401)")
            if status != 200:
                text = body[:200].decode(errors="replace")
                raise ExecutorProtocolError(f"réponse {status} sur {path} : {text}")
            try:
                return json.loads(body)
            except ValueError as exc:
                raise ExecutorProtocolError(f"corps non JSON sur {path}") from exc
        raise ExecutorUnavailable(f"{method} {path} : {last} ({attempts} tentative(s))")

    @staticmethod
    def _parse(adapter: Any, data: Any, path: str) -> Any:
        try:
            return adapter.validate_python(data) if isinstance(adapter, TypeAdapter) \
                else adapter.model_validate(data)
        except ValidationError as exc:
            raise ExecutorProtocolError(f"réponse hors contrat sur {path} : {exc}") from exc

    @staticmethod
    def _audit_path(audit_id: str) -> str:
        if not isinstance(audit_id, str) or not _AUDIT_ID.fullmatch(audit_id):
            raise InvalidRequest(f"audit_id invalide : {audit_id!r}")
        return quote(audit_id, safe="")

    # --------------------------------------------------------------- routes
    def health(self) -> HealthResponse:
        return self._parse(HealthResponse, self._call("GET", "/health", retry=True), "/health")

    def list_tools(self) -> list[ToolSpec]:
        return self._parse(_TOOLS, self._call("GET", "/tools", retry=True), "/tools")

    def execute(self, req: ExecuteRequest) -> ExecuteResponse:
        data = self._call("POST", "/execute", retry=True, json=req.model_dump(mode="json"))
        resp = self._parse(ExecuteResponse, data, "/execute")
        if resp.request_id != req.request_id:
            raise ExecutorProtocolError(
                f"request_id renvoyé {resp.request_id!r} différent de {req.request_id!r}")
        return resp

    def decide_approval(self, audit_id: str, decision: str, approver: str) -> ExecuteResponse:
        path = f"/approvals/{self._audit_path(audit_id)}"
        body = ApprovalRequest(decision=decision, approver=approver)
        data = self._call("POST", path, retry=False, json=body.model_dump())
        return self._parse(ExecuteResponse, data, "/approvals")

    def undo(self, audit_id: str) -> ExecuteResponse:
        path = f"/undo/{self._audit_path(audit_id)}"
        return self._parse(ExecuteResponse, self._call("POST", path, retry=False), "/undo")

    def audit(self, ticket_id: str | None = None) -> list[AuditEntry]:
        params = {"ticket_id": ticket_id} if ticket_id is not None else None
        return self._parse(_AUDIT, self._call("GET", "/audit", retry=True, params=params), "/audit")

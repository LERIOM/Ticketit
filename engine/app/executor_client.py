"""SEUL point d'accès au module d'exécution de Florent (contrat v1).

Règles :
- délai de `executor_timeout_s` (5 s) par appel ;
- `/v1/execute` et les lectures : une seule nouvelle tentative, avec le MÊME
  request_id (l'executor est idempotent), si pas de réponse ou erreur 5xx ;
- approbations et annulations : jamais rejouées automatiquement ;
- toute erreur lève `ExecutorError` : l'appelant escalade le ticket, il n'y a
  jamais d'action « par défaut ».
"""
from typing import Any

import httpx
from pydantic import TypeAdapter, ValidationError

from .config import settings
from .models import ApprovalRequest, AuditEntry, ExecuteRequest, ExecuteResponse, ToolSpec


class ExecutorError(Exception):
    """Échec d'un appel à l'executor : le ticket doit être escaladé."""


class ExecutorUnavailable(ExecutorError):
    """Pas de réponse exploitable après la nouvelle tentative (délai, réseau, 5xx)."""


class ExecutorProtocolError(ExecutorError):
    """Réponse contraire au contrat v1 (401, 422, corps invalide…)."""


_TOOLS = TypeAdapter(list[ToolSpec])
_AUDIT = TypeAdapter(list[AuditEntry])


class ExecutorClient:
    def __init__(self, base_url: str | None = None, api_key: str | None = None,
                 timeout_s: float | None = None, http: httpx.Client | None = None) -> None:
        self.timeout_s = settings.executor_timeout_s if timeout_s is None else timeout_s
        self._headers = {"X-API-Key": settings.executor_api_key if api_key is None else api_key}
        self._http = http or httpx.Client(base_url=base_url or settings.executor_url,
                                          timeout=self.timeout_s)

    # ------------------------------------------------------------ transport
    def _call(self, method: str, path: str, *, retry: bool, **kw: Any) -> Any:
        attempts = 2 if retry else 1
        last = "aucune tentative"
        for _ in range(attempts):
            try:
                r = self._http.request(method, f"/v1{path}", headers=self._headers, **kw)
            except httpx.TimeoutException:
                last = f"délai de {self.timeout_s:g} s dépassé"
                continue
            except httpx.TransportError as exc:
                last = f"executor injoignable ({exc.__class__.__name__})"
                continue
            if r.status_code >= 500:
                last = f"erreur serveur {r.status_code}"
                continue
            if r.status_code == 401:
                raise ExecutorProtocolError("clé API refusée par l'executor (401)")
            if r.status_code != 200:
                raise ExecutorProtocolError(f"réponse {r.status_code} sur {path} : {r.text[:200]}")
            try:
                return r.json()
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

    # --------------------------------------------------------------- routes
    def health(self) -> dict[str, Any]:
        return self._call("GET", "/health", retry=True)

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
        body = ApprovalRequest(decision=decision, approver=approver)
        data = self._call("POST", f"/approvals/{audit_id}", retry=False, json=body.model_dump())
        return self._parse(ExecuteResponse, data, "/approvals")

    def undo(self, audit_id: str) -> ExecuteResponse:
        return self._parse(ExecuteResponse, self._call("POST", f"/undo/{audit_id}", retry=False), "/undo")

    def audit(self, ticket_id: str | None = None) -> list[AuditEntry]:
        params = {"ticket_id": ticket_id} if ticket_id else None
        return self._parse(_AUDIT, self._call("GET", "/audit", retry=True, params=params), "/audit")

"""Faux module d'exécution, conforme au contrat v1 (contracts/executor_v1.openapi.yaml).

Mêmes routes, même format de réponse et même idempotence que le vrai module de
Florent, avec une version simplifiée du tableau des niveaux. L'engine choisit
entre le faux et le vrai uniquement par EXECUTOR_URL.
"""
import math
import os
import secrets
import time
import uuid
from typing import Any, Literal

from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator

from . import catalog
from .state import STATE, TargetNotFound, new_request_id

API_KEY = os.environ.get("EXECUTOR_API_KEY", "change-me")
# Pour démontrer l'escalade sur délai dépassé : MOCK_EXECUTE_DELAY_S=6
EXECUTE_DELAY_S = float(os.environ.get("MOCK_EXECUTE_DELAY_S", "0"))


def check_key(x_api_key: str | None = Header(default=None)) -> None:
    if not x_api_key or not secrets.compare_digest(x_api_key, API_KEY):
        raise HTTPException(status_code=401, detail="invalid api key")


# Pas de /docs ni /openapi.json publics : seules les routes du contrat existent.
app = FastAPI(title="mock executor", version="1.0", dependencies=[Depends(check_key)],
              docs_url=None, redoc_url=None, openapi_url=None)


def _finite(o: Any) -> Any:
    if isinstance(o, float) and not math.isfinite(o):
        return str(o)
    if isinstance(o, dict):
        return {k: _finite(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_finite(v) for v in o]
    return o


@app.exception_handler(RequestValidationError)
async def _invalid_request(_: Request, exc: RequestValidationError) -> JSONResponse:
    """422 propre même si l'entrée contient NaN / Infinity (sinon erreur 500)."""
    return JSONResponse(status_code=422, content={"detail": _finite(jsonable_encoder(exc.errors()))})


# ----------------------------------------------------------------- schémas

class ExecuteRequest(BaseModel):
    request_id: str
    ticket_id: str
    tool: str
    params: dict[str, Any]
    confidence: float = Field(ge=0, le=1, allow_inf_nan=False)
    justification: str

    @field_validator("request_id")
    @classmethod
    def _uuid(cls, v: str) -> str:
        # Forme canonique exigée : sinon le même UUID écrit en majuscules ou sans
        # tirets passerait l'idempotence et l'action serait exécutée plusieurs fois.
        if v != str(uuid.UUID(v)):
            raise ValueError("request_id doit être un UUID canonique (minuscules, avec tirets)")
        return v


class ApprovalRequest(BaseModel):
    decision: Literal["approve", "reject"]
    approver: str = Field(min_length=1)


Status = Literal["executed", "refused", "pending_approval", "failed"]


class ExecuteResponse(BaseModel):
    request_id: str
    status: Status
    level: int = Field(ge=0, le=3)
    reason: str
    audit_id: str
    result: dict[str, Any] | None
    undo_available: bool


class AuditEntry(BaseModel):
    audit_id: str
    timestamp: str
    request_id: str
    ticket_id: str
    tool: str
    params: dict[str, Any]
    confidence: float
    justification: str
    level: int
    status: Status
    reason: str
    approver: str | None
    undo_of: str | None


class Tool(BaseModel):
    name: str
    level: int = Field(ge=0, le=3)
    description: str
    params_schema: dict[str, Any]
    reversible: bool


class Health(BaseModel):
    status: Literal["ok"]
    version: str


# -------------------------------------------------------------- décisions

def _decide(req: ExecuteRequest) -> tuple[int, Status, str]:
    """Version simplifiée du tableau des niveaux : (niveau, status, raison)."""
    tool = catalog.TOOLS_BY_NAME.get(req.tool)
    if tool is None:
        return 3, "refused", f"Outil inconnu ou interdit ({req.tool}) : niveau 3, jamais exécuté"
    level = tool["level"]
    invalid = catalog.validate_params(tool, req.params)
    if invalid:
        return level, "refused", f"Paramètres invalides pour {req.tool} : {invalid}"
    if level == 0:
        return 0, "executed", "Niveau 0, lecture seule"
    if level == 2:
        return 2, "pending_approval", "Niveau 2 : validation humaine obligatoire"
    th = catalog.L1_THRESHOLD
    if req.tool == "block_ip" and not catalog.ip_auto_blockable(req.params["ip"]):
        return 1, "pending_approval", "Niveau 1, IP privée, de bouclage ou protégée : validation humaine"
    if req.tool == "force_password_reset" and req.params["username"].casefold() in catalog.PROTECTED_ACCOUNTS:
        return 1, "pending_approval", "Niveau 1, compte protégé : validation humaine"
    if req.confidence < th:
        return 1, "pending_approval", f"Niveau 1, confiance {req.confidence:.2f} < {th:.2f}"
    return 1, "executed", f"Niveau 1, confiance {req.confidence:.2f} >= {th:.2f}, cible non protégée"


def _reversible(tool: str) -> bool:
    return bool(catalog.TOOLS_BY_NAME.get(tool, {}).get("reversible"))


def _run(request_id: str, tool: str, params: dict[str, Any], reason: str) -> tuple[Status, str, dict | None]:
    try:
        return "executed", reason, STATE.run(request_id, tool, params)
    except TargetNotFound as exc:
        return "failed", f"Échec de l'exécution : {exc}", None


def _response(entry: dict[str, Any], result: dict | None) -> dict[str, Any]:
    undo = entry["status"] == "executed" and entry["undo_of"] is None and _reversible(entry["tool"])
    return {"request_id": entry["request_id"], "status": entry["status"], "level": entry["level"],
            "reason": entry["reason"], "audit_id": entry["audit_id"], "result": result,
            "undo_available": undo}


# ------------------------------------------------------------------ routes

@app.get("/v1/health", response_model=Health)
def health() -> dict:
    return {"status": "ok", "version": "1.0"}


@app.get("/v1/tools", response_model=list[Tool])
def tools() -> list[dict]:
    return catalog.TOOLS


@app.post("/v1/execute", response_model=ExecuteResponse)
def execute(req: ExecuteRequest) -> dict:
    if EXECUTE_DELAY_S:
        time.sleep(EXECUTE_DELAY_S)
    with STATE.lock:
        if req.request_id in STATE.responses:            # idempotence
            return STATE.responses[req.request_id]
        level, status, reason = _decide(req)
        result = None
        if status == "executed":
            status, reason, result = _run(req.request_id, req.tool, req.params, reason)
        entry = STATE.append_audit(request_id=req.request_id, ticket_id=req.ticket_id, tool=req.tool,
                                   params=req.params, confidence=req.confidence,
                                   justification=req.justification, level=level,
                                   status=status, reason=reason)
        resp = _response(entry, result)
        STATE.responses[req.request_id] = resp
        return resp


def _refused_unknown(audit_id: str, what: str) -> dict:
    return {"request_id": new_request_id(), "status": "refused", "level": 3,
            "reason": f"{what} : audit_id inconnu ({audit_id})", "audit_id": audit_id,
            "result": None, "undo_available": False}


@app.post("/v1/approvals/{audit_id}", response_model=ExecuteResponse)
def approve(audit_id: str, body: ApprovalRequest) -> dict:
    with STATE.lock:
        pending = STATE.find_audit(audit_id)
        if pending is None:
            return _refused_unknown(audit_id, "Validation impossible")
        base = {k: pending[k] for k in ("request_id", "ticket_id", "tool", "params",
                                        "confidence", "justification", "level")}
        if pending["status"] != "pending_approval" or audit_id in STATE.decided:
            entry = STATE.append_audit(**base, status="refused", approver=body.approver,
                                       reason=f"Aucune action en attente pour {audit_id}")
            return _response(entry, None)
        STATE.decided.add(audit_id)
        result = None
        if body.decision == "reject":
            status, reason = "refused", f"Rejeté par {body.approver}"
        else:
            status, reason, result = _run(pending["request_id"], pending["tool"], pending["params"],
                                          f"Validé par {body.approver} (niveau {pending['level']})")
        entry = STATE.append_audit(**base, status=status, reason=reason, approver=body.approver)
        return _response(entry, result)


@app.post("/v1/undo/{audit_id}", response_model=ExecuteResponse)
def undo(audit_id: str) -> dict:
    with STATE.lock:
        target = STATE.find_audit(audit_id)
        if target is None:
            return _refused_unknown(audit_id, "Annulation impossible")
        base = {k: target[k] for k in ("ticket_id", "tool", "params", "confidence",
                                       "justification", "level")}
        if target["status"] != "executed" or target["undo_of"] is not None \
                or not _reversible(target["tool"]):
            reason, result = f"Action non réversible ({target['tool']}, {target['status']})", None
            status = "refused"
        elif audit_id in STATE.undone:
            reason, result, status = f"Action {audit_id} déjà annulée", None, "refused"
        else:
            STATE.undone.add(audit_id)
            result = STATE.undo(target["tool"], target["params"])
            reason, status = f"Annulation de {audit_id}", "executed"
        entry = STATE.append_audit(**base, request_id=new_request_id(), status=status, reason=reason,
                                   undo_of=audit_id)
        return _response(entry, result)


@app.get("/v1/audit", response_model=list[AuditEntry])
def audit(ticket_id: str | None = None) -> list[dict]:
    with STATE.lock:
        entries = [e for e in STATE.audit if ticket_id is None or e["ticket_id"] == ticket_id]
        return list(reversed(entries))

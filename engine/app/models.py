"""Modèles de données partagés par tout le moteur.

Le texte stocké dans un Ticket est TOUJOURS le texte masqué. Le texte d'origine
et la table de pseudonymes restent côté serveur (security/, étape 3).
"""
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field, model_validator


def _now() -> datetime:
    return datetime.now(timezone.utc)


# ---------------------------------------------------------------- Ticket

class Source(str, Enum):
    USER = "user"      # POST /tickets
    ALERT = "alert"    # POST /alerts (Wazuh / Suricata)


class Category(str, Enum):
    """Liste fermée (proposition S1, à valider)."""
    ACCES_COMPTE = "acces_compte"
    MOT_DE_PASSE = "mot_de_passe"
    MESSAGERIE = "messagerie"
    RESEAU = "reseau"
    LOGICIEL = "logiciel"
    MATERIEL = "materiel"
    IMPRESSION = "impression"
    PHISHING = "phishing"
    MALWARE = "malware"
    BRUTEFORCE = "bruteforce"
    SCAN_RESEAU = "scan_reseau"
    FUITE_DONNEES = "fuite_donnees"
    AUTRE = "autre"


class Priority(str, Enum):
    P1 = "P1"  # critique
    P2 = "P2"
    P3 = "P3"
    P4 = "P4"  # faible


class TicketStatus(str, Enum):
    NEW = "new"
    PROCESSING = "processing"
    RESOLVED = "resolved"
    PENDING_APPROVAL = "pending_approval"
    ESCALATED = "escalated"
    CLOSED = "closed"


class TechnicalEntities(BaseModel):
    """Identifiants nécessaires aux actions, gardés HORS du texte envoyé au LLM."""
    external_ips: list[str] = Field(default_factory=list)
    hostnames: list[str] = Field(default_factory=list)
    usernames: list[str] = Field(default_factory=list)


class Classification(BaseModel):
    category: Category
    priority: Priority
    automatable: bool


class Ticket(BaseModel):
    id: str = Field(default_factory=lambda: f"T-{uuid4().hex[:8]}")
    source: Source
    created_at: datetime = Field(default_factory=_now)
    language: Literal["fr", "en"] | None = None
    text_masked: str
    entities: TechnicalEntities = Field(default_factory=TechnicalEntities)
    alert_ref: str | None = None          # ex. "W-889" pour une alerte
    suspicious: bool = False              # injection de prompt détectée
    suspicious_reasons: list[str] = Field(default_factory=list)
    classification: Classification | None = None
    decision: "Decision | None" = None
    status: TicketStatus = TicketStatus.NEW
    final_answer: str | None = None       # réponse de l'agent ou de l'humain


# --------------------------------------------------------------- Decision

class SourceRef(BaseModel):
    """Élément de la base de connaissance qui appuie une réponse."""
    node_id: str
    kind: Literal["Solution", "Document", "Probleme", "Ticket"]
    title: str
    score: float = Field(ge=0, le=1)


class ProposedAction(BaseModel):
    tool: str
    params: dict[str, Any]


class DecisionType(str, Enum):
    RESPOND = "respond"
    ACT = "act"
    ESCALATE = "escalate"


class Decision(BaseModel):
    """Sortie structurée du nœud `decide`.

    Les règles dures (seuil, ticket suspect) sont appliquées par le code de
    l'agent ; ici on garantit seulement la cohérence de l'objet.
    """
    type: DecisionType
    confidence: float = Field(ge=0, le=1)
    sources: list[SourceRef] = Field(default_factory=list)
    justification: str = Field(min_length=1)
    answer: str | None = None
    action: ProposedAction | None = None

    @model_validator(mode="after")
    def _coherent(self) -> "Decision":
        if self.type == DecisionType.RESPOND:
            if not self.sources:
                raise ValueError("respond exige au moins une source")
            if not self.answer:
                raise ValueError("respond exige une réponse")
        if self.type == DecisionType.ACT and self.action is None:
            raise ValueError("act exige une action proposée")
        if self.type != DecisionType.ACT and self.action is not None:
            raise ValueError("seul act peut porter une action")
        return self


Ticket.model_rebuild()


# ------------------------------------------- Contrat executor v1 (miroir)

ExecStatus = Literal["executed", "refused", "pending_approval", "failed"]


class ToolSpec(BaseModel):
    name: str
    level: int = Field(ge=0, le=3)
    description: str
    params_schema: dict[str, Any]
    reversible: bool


class ExecuteRequest(BaseModel):
    request_id: str = Field(default_factory=lambda: str(uuid4()))
    ticket_id: str
    tool: str
    params: dict[str, Any]
    confidence: float = Field(ge=0, le=1)
    justification: str


class ExecuteResponse(BaseModel):
    request_id: str
    status: ExecStatus
    level: int
    reason: str
    audit_id: str
    result: dict[str, Any] | None
    undo_available: bool


class ApprovalRequest(BaseModel):
    decision: Literal["approve", "reject"]
    approver: str = Field(min_length=1)


class AuditEntry(BaseModel):
    audit_id: str
    timestamp: datetime
    request_id: str
    ticket_id: str
    tool: str
    params: dict[str, Any]
    confidence: float
    justification: str
    level: int
    status: ExecStatus
    reason: str
    approver: str | None
    undo_of: str | None

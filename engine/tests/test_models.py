import pytest
from pydantic import ValidationError

from app.models import (
    Category, Decision, DecisionType, ExecuteResponse, ProposedAction,
    Source, SourceRef, Ticket,
)

SRC = SourceRef(node_id="S-1", kind="Solution", title="Réinitialiser le VPN", score=0.9)


def test_ticket_defaults():
    t = Ticket(source=Source.USER, text_masked="Mon VPN ne marche plus, <PERSON_1>")
    assert t.id.startswith("T-")
    assert t.status == "new"
    assert t.entities.external_ips == []


def test_category_is_closed_list():
    with pytest.raises(ValueError):
        Category("inconnue")


def test_respond_requires_source():
    with pytest.raises(ValidationError):
        Decision(type=DecisionType.RESPOND, confidence=0.9, justification="x", answer="ok")
    Decision(type=DecisionType.RESPOND, confidence=0.9, justification="x", answer="ok", sources=[SRC])


def test_act_requires_action_and_only_act_has_one():
    with pytest.raises(ValidationError):
        Decision(type=DecisionType.ACT, confidence=0.9, justification="x")
    action = ProposedAction(tool="block_ip", params={"ip": "203.0.113.5", "duration_hours": 24})
    Decision(type=DecisionType.ACT, confidence=0.9, justification="x", action=action)
    with pytest.raises(ValidationError):
        Decision(type=DecisionType.ESCALATE, confidence=0.2, justification="x", action=action)


def test_confidence_bounds():
    with pytest.raises(ValidationError):
        Decision(type=DecisionType.ESCALATE, confidence=1.2, justification="x")


def test_execute_response_matches_contract_example():
    r = ExecuteResponse.model_validate({
        "request_id": "uuid-v4", "status": "executed", "level": 1,
        "reason": "Niveau 1, confiance 0.91 >= 0.80, cible non protégée",
        "audit_id": "A-000456", "result": {"blocked_until": "2026-11-03T14:00:00Z"},
        "undo_available": True,
    })
    assert r.status == "executed"
    with pytest.raises(ValidationError):
        ExecuteResponse.model_validate({**r.model_dump(), "status": "done"})

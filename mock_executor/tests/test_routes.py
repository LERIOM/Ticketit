"""Comportement du faux executor : niveaux, idempotence, approbations, annulation, audit."""
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.state import STATE

from .conftest import exec_body


def test_api_key_required():
    anon = TestClient(app)
    for method, path in [("get", "/v1/health"), ("get", "/v1/tools"), ("get", "/v1/audit"),
                         ("post", "/v1/undo/A-000001")]:
        assert getattr(anon, method)(path).status_code == 401
    assert TestClient(app, headers={"X-API-Key": "mauvaise"}).get("/v1/health").status_code == 401


def test_schema_violation_is_422(client):
    assert client.post("/v1/execute", json={"tool": "block_ip"}).status_code == 422
    bad_conf = exec_body("block_ip", {"ip": "203.0.113.5", "duration_hours": 1}, confidence=1.5)
    assert client.post("/v1/execute", json=bad_conf).status_code == 422
    bad_id = {**exec_body("logs_search", {}), "request_id": "pas-un-uuid"}
    assert client.post("/v1/execute", json=bad_id).status_code == 422
    assert client.post("/v1/approvals/A-1", json={"decision": "peut-être", "approver": "x"}).status_code == 422


# ------------------------------------------------------------ tableau des niveaux

@pytest.mark.parametrize("tool,params,conf,status,level", [
    ("logs_search", {"query": "sshd", "since_minutes": 60}, 0.1, "executed", 0),
    ("account_info", {"username": "j.martin"}, 0.1, "executed", 0),
    ("block_ip", {"ip": "203.0.113.5", "duration_hours": 24}, 0.91, "executed", 1),
    ("block_ip", {"ip": "203.0.113.5", "duration_hours": 24}, 0.80, "executed", 1),   # seuil inclus
    ("block_ip", {"ip": "203.0.113.5", "duration_hours": 24}, 0.79, "pending_approval", 1),
    ("block_ip", {"ip": "10.0.0.12", "duration_hours": 1}, 0.99, "pending_approval", 1),
    ("block_ip", {"ip": "127.0.0.1", "duration_hours": 1}, 0.99, "pending_approval", 1),
    ("block_ip", {"ip": "192.168.1.10", "duration_hours": 1}, 0.99, "pending_approval", 1),
    ("force_password_reset", {"username": "j.martin"}, 0.85, "executed", 1),
    ("force_password_reset", {"username": "admin"}, 0.99, "pending_approval", 1),
    ("isolate_host", {"hostname": "PC-COMPTA-07"}, 0.99, "pending_approval", 2),
    ("disable_account", {"username": "admin"}, 0.99, "pending_approval", 2),
    ("delete_data", {"path": "/srv"}, 0.99, "refused", 3),
    ("modify_firewall_policy", {"rule": "allow all"}, 0.99, "refused", 3),
])
def test_level_table(client, tool, params, conf, status, level):
    r = client.post("/v1/execute", json=exec_body(tool, params, conf)).json()
    assert (r["status"], r["level"]) == (status, level), r["reason"]


@pytest.mark.parametrize("params", [
    {"ip": "0.0.0.0/0", "duration_hours": 1},
    {"ip": "203.0.113.5", "duration_hours": 48},
    {"ip": "203.0.113.5"},
    {"ip": "203.0.113.5", "duration_hours": "24"},
    {"ip": "203.0.113.5", "duration_hours": 1, "extra": True},
])
def test_invalid_params_are_refused_not_http_errors(client, params):
    r = client.post("/v1/execute", json=exec_body("block_ip", params))
    assert r.status_code == 200
    assert r.json()["status"] == "refused"
    assert STATE.blocked_ips == {}


def test_injection_in_username_refused(client):
    r = client.post("/v1/execute", json=exec_body("account_info", {"username": "admin; DROP TABLE"})).json()
    assert r["status"] == "refused"


def test_unknown_target_fails(client):
    r = client.post("/v1/execute", json=exec_body("force_password_reset", {"username": "fantome"})).json()
    assert r["status"] == "failed" and r["result"] is None and not r["undo_available"]


def test_logs_search_finds_integration_scenarios(client):
    r = client.post("/v1/execute", json=exec_body("logs_search", {"query": "203.0.113.5",
                                                                  "since_minutes": 60})).json()
    assert r["result"]["count"] == 12


# ------------------------------------------------------------------ idempotence

def test_same_request_id_returns_same_response_without_rerun(client):
    body = exec_body("block_ip", {"ip": "203.0.113.5", "duration_hours": 24})
    first = client.post("/v1/execute", json=body).json()
    second = client.post("/v1/execute", json=body).json()
    assert first == second
    assert STATE.runs[body["request_id"]] == 1
    assert len(client.get("/v1/audit").json()) == 1


# ---------------------------------------------------------- approbations / undo

def test_approve_then_undo(client):
    p = client.post("/v1/execute", json=exec_body("disable_account", {"username": "j.martin"})).json()
    assert p["status"] == "pending_approval" and STATE.accounts["j.martin"]["active"]
    a = client.post(f"/v1/approvals/{p['audit_id']}",
                    json={"decision": "approve", "approver": "analyste.dupont"}).json()
    assert a["status"] == "executed" and a["undo_available"]
    assert a["request_id"] == p["request_id"] and a["audit_id"] != p["audit_id"]
    assert not STATE.accounts["j.martin"]["active"]
    u = client.post(f"/v1/undo/{a['audit_id']}").json()
    assert u["status"] == "executed" and not u["undo_available"]
    assert STATE.accounts["j.martin"]["active"]
    again = client.post(f"/v1/undo/{a['audit_id']}").json()
    assert again["status"] == "refused"


def test_reject_and_double_decision(client):
    p = client.post("/v1/execute", json=exec_body("isolate_host", {"hostname": "SRV-WEB-01"})).json()
    r = client.post(f"/v1/approvals/{p['audit_id']}", json={"decision": "reject", "approver": "a.b"}).json()
    assert r["status"] == "refused" and "a.b" in r["reason"]
    twice = client.post(f"/v1/approvals/{p['audit_id']}", json={"decision": "approve", "approver": "a.b"}).json()
    assert twice["status"] == "refused"
    assert not STATE.hosts["SRV-WEB-01"]["isolated"]


def test_cannot_approve_executed_or_unknown(client):
    e = client.post("/v1/execute", json=exec_body("account_info", {"username": "j.martin"})).json()
    assert client.post(f"/v1/approvals/{e['audit_id']}",
                       json={"decision": "approve", "approver": "x"}).json()["status"] == "refused"
    assert client.post("/v1/approvals/A-999999",
                       json={"decision": "approve", "approver": "x"}).json()["status"] == "refused"


def test_undo_non_reversible_refused(client):
    e = client.post("/v1/execute", json=exec_body("logs_search", {"query": "x", "since_minutes": 5})).json()
    assert client.post(f"/v1/undo/{e['audit_id']}").json()["status"] == "refused"


# ------------------------------------------------------------------------ audit

def test_audit_filtered_newest_first_with_all_fields(client):
    client.post("/v1/execute", json=exec_body("account_info", {"username": "j.martin"}, ticket_id="T-1"))
    client.post("/v1/execute", json=exec_body("account_info", {"username": "a.durand"}, ticket_id="T-2"))
    client.post("/v1/execute", json=exec_body("logs_search", {"query": "x", "since_minutes": 5}, ticket_id="T-1"))
    entries = client.get("/v1/audit", params={"ticket_id": "T-1"}).json()
    assert [e["tool"] for e in entries] == ["logs_search", "account_info"]
    assert entries[0]["timestamp"] >= entries[1]["timestamp"]
    assert set(entries[0]) == {"audit_id", "timestamp", "request_id", "ticket_id", "tool", "params",
                               "confidence", "justification", "level", "status", "reason",
                               "approver", "undo_of"}


def test_audit_is_read_only():
    routes = {(r.path, m) for r in app.routes for m in getattr(r, "methods", ())}
    assert not any(m in {"PUT", "PATCH", "DELETE"} for _, m in routes)


# ------------------------------------------------- jeu d'intégration commun

def test_trap_case_never_executed(client):
    ip = client.post("/v1/execute", json=exec_body("block_ip", {"ip": "10.0.0.12", "duration_hours": 24},
                                                   confidence=1.0)).json()
    acc = client.post("/v1/execute", json=exec_body("disable_account", {"username": "admin"},
                                                    confidence=1.0)).json()
    assert ip["status"] in {"refused", "pending_approval"}
    assert acc["status"] in {"refused", "pending_approval"}
    assert STATE.blocked_ips == {} and STATE.accounts["admin"]["active"]

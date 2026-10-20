"""Régressions trouvées par la recette adversariale du 2026-10-20 (blocs A et B)."""
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.state import STATE

from .conftest import exec_body


@pytest.mark.parametrize("ip", [
    "::ffff:10.0.0.12", "::ffff:127.0.0.1", "::ffff:192.168.1.1", "::ffff:7f00:1",
    "::ffff:203.0.113.250",            # IP protégée écrite en IPv6
    "::10.0.0.1", "::", "::1", "ff02::1", "fec0::1", "fd00::1", "fe80::1",
    "64:ff9b::a00:1",                  # NAT64 de 10.0.0.1
    "2002:0a00:0001::",                # 6to4 de 10.0.0.1
    "100.64.0.1", "192.0.0.1", "198.18.0.1", "240.0.0.1",
])
def test_non_public_ip_never_auto_blocked(client, ip):
    r = client.post("/v1/execute", json=exec_body("block_ip", {"ip": ip, "duration_hours": 1},
                                                  confidence=1.0)).json()
    assert r["status"] == "pending_approval", (ip, r["reason"])
    assert STATE.blocked_ips == {}


@pytest.mark.parametrize("ip", ["203.0.113.5", "8.8.8.8", "2001:db8::1", "2606:4700::1111"])
def test_public_ip_still_auto_blocked(client, ip):
    r = client.post("/v1/execute", json=exec_body("block_ip", {"ip": ip, "duration_hours": 1})).json()
    assert r["status"] == "executed"


def test_ipv6_zone_refused(client):
    r = client.post("/v1/execute", json=exec_body("block_ip", {"ip": "2001:db8::1%eth0",
                                                               "duration_hours": 1})).json()
    assert r["status"] == "refused"


@pytest.mark.parametrize("transform", [str.upper, lambda u: u.replace("-", ""), lambda u: "{" + u + "}"])
def test_non_canonical_request_id_rejected(client, transform):
    body = exec_body("account_info", {"username": "j.martin"})
    body["request_id"] = transform(str(uuid4()))
    assert client.post("/v1/execute", json=body).status_code == 422


@pytest.mark.parametrize("conf", ["NaN", "Infinity", "-Infinity"])
def test_non_finite_confidence_is_422_not_500(client, conf):
    raw = ('{"request_id": "%s", "ticket_id": "T-1", "tool": "account_info", '
           '"params": {"username": "j.martin"}, "confidence": %s, "justification": "x"}') % (uuid4(), conf)
    r = client.post("/v1/execute", content=raw, headers={"Content-Type": "application/json"})
    assert r.status_code == 422


def test_protected_account_is_case_insensitive(client):
    r = client.post("/v1/execute", json=exec_body("force_password_reset", {"username": "ADMIN"})).json()
    assert r["status"] == "pending_approval"


def test_no_public_docs():
    anon = TestClient(app)
    for path in ("/docs", "/redoc", "/openapi.json"):
        assert anon.get(path).status_code in (401, 404)

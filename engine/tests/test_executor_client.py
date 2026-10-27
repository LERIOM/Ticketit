"""Client executor : chaque status, délai dépassé, une seule nouvelle tentative avec le
même request_id, erreurs de contrat, puis intégration avec le faux executor."""
import json

import httpx
import pytest

from app.executor_client import (
    ExecutorClient, ExecutorProtocolError, ExecutorUnavailable, InvalidRequest,
)
from app.models import ExecuteRequest

REQ = ExecuteRequest(ticket_id="T-123", tool="block_ip",
                     params={"ip": "203.0.113.5", "duration_hours": 24},
                     confidence=0.91, justification="12 échecs SSH en 2 min (W-889)")


def _resp(status: str, request_id: str = REQ.request_id, **kw) -> dict:
    return {"request_id": request_id, "status": status, "level": 1, "reason": "r",
            "audit_id": "A-000001", "result": None, "undo_available": False, **kw}


def scripted(*steps):
    """Client dont le transport rejoue `steps` (réponse JSON, code, ou exception)."""
    calls: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        step = steps[min(len(calls), len(steps)) - 1]
        if isinstance(step, Exception):
            raise step
        if isinstance(step, int):
            return httpx.Response(step)
        return httpx.Response(200, json=step)

    http = httpx.Client(base_url="http://executor:8100", transport=httpx.MockTransport(handler))
    return ExecutorClient(api_key="k", timeout_s=5, http=http), calls


@pytest.mark.parametrize("status", ["executed", "refused", "pending_approval", "failed"])
def test_each_status_is_returned(status):
    client, calls = scripted(_resp(status))
    assert client.execute(REQ).status == status
    assert len(calls) == 1
    assert calls[0].headers["X-API-Key"] == "k"
    assert calls[0].url.path == "/v1/execute"


def test_default_timeout_is_5s():
    assert ExecutorClient().timeout_s == 5.0


def test_timeout_twice_raises_unavailable_after_one_retry_same_request_id():
    client, calls = scripted(httpx.ReadTimeout("lent"), httpx.ReadTimeout("lent"))
    with pytest.raises(ExecutorUnavailable, match="délai"):
        client.execute(REQ)
    assert len(calls) == 2
    ids = {json.loads(c.content)["request_id"] for c in calls}
    assert ids == {REQ.request_id}


def test_timeout_then_success():
    client, calls = scripted(httpx.ConnectTimeout("lent"), _resp("executed"))
    assert client.execute(REQ).status == "executed"
    assert len(calls) == 2


def test_connection_refused_and_5xx_are_unavailable():
    client, calls = scripted(httpx.ConnectError("refus"), 503)
    with pytest.raises(ExecutorUnavailable):
        client.execute(REQ)
    assert len(calls) == 2


def test_401_is_not_retried():
    client, calls = scripted(401)
    with pytest.raises(ExecutorProtocolError, match="401"):
        client.execute(REQ)
    assert len(calls) == 1


@pytest.mark.parametrize("body", [
    _resp("done"),                               # status hors contrat
    {"status": "executed"},                      # champs manquants
    _resp("executed", request_id="autre-id"),    # mauvais request_id
])
def test_out_of_contract_body_is_protocol_error(body):
    client, _ = scripted(body)
    with pytest.raises(ExecutorProtocolError):
        client.execute(REQ)


def test_approvals_and_undo_are_never_replayed():
    client, calls = scripted(httpx.ReadTimeout("lent"))
    with pytest.raises(ExecutorUnavailable):
        client.decide_approval("A-000001", "approve", "analyste.dupont")
    with pytest.raises(ExecutorUnavailable):
        client.undo("A-000001")
    assert len(calls) == 2  # un appel chacun


# ------------------------------------------------- intégration avec le faux executor

@pytest.fixture
def real(mock_executor):
    http, state = mock_executor
    from tests.conftest import _load_mock_executor
    main, _ = _load_mock_executor()
    return ExecutorClient(api_key=main.API_KEY, http=http), state


def test_mock_catalog(real):
    client, _ = real
    assert {t.name for t in client.list_tools()} == {
        "logs_search", "account_info", "block_ip", "force_password_reset",
        "isolate_host", "disable_account"}
    assert client.health().status == "ok"


def test_idempotence_against_mock(real):
    client, state = real
    first, second = client.execute(REQ), client.execute(REQ)
    assert first == second and first.status == "executed"
    assert state.runs[REQ.request_id] == 1


def test_ssh_bruteforce_then_undo_and_audit(real):
    client, state = real
    r = client.execute(REQ.model_copy(update={"request_id": "4c1c1fd8-21e5-4fa2-9b0d-0f0b0c0a0001"}))
    assert r.status == "executed" and "203.0.113.5" in state.blocked_ips
    u = client.undo(r.audit_id)
    assert u.status == "executed" and "203.0.113.5" not in state.blocked_ips
    entries = client.audit("T-123")
    assert [e.undo_of for e in entries] == [r.audit_id, None]


def test_trap_case_pending_then_rejected(real):
    client, state = real
    trap = ExecuteRequest(ticket_id="T-9", tool="disable_account", params={"username": "admin"},
                          confidence=1.0, justification="demande du ticket")
    p = client.execute(trap)
    assert p.status == "pending_approval"
    rejected = client.decide_approval(p.audit_id, "reject", "analyste.dupont")
    assert rejected.status == "refused" and state.accounts["admin"]["active"]


def test_wrong_key_against_mock(mock_executor):
    http, _ = mock_executor
    with pytest.raises(ExecutorProtocolError):
        ExecutorClient(api_key="mauvaise", http=http).list_tools()


# ------------------------------------- régressions de la recette du 2026-10-20

@pytest.mark.parametrize("audit_id", ["x/../../undo/A-000001", "A-1?x=1", "A-1#x", "", "A-1%2F"])
def test_trapped_audit_id_never_sent(audit_id):
    client, calls = scripted(_resp("executed"))
    with pytest.raises(InvalidRequest):
        client.decide_approval(audit_id, "reject", "analyste")
    with pytest.raises(InvalidRequest):
        client.undo(audit_id)
    assert calls == []


def test_trapped_audit_id_cannot_undo_against_mock(real):
    client, state = real
    r = client.execute(REQ)
    with pytest.raises(InvalidRequest):
        client.decide_approval(f"x/../../undo/{r.audit_id}", "reject", "pirate")
    assert "203.0.113.5" in state.blocked_ips          # toujours bloquée


def test_corrupted_body_is_retried_then_unavailable():
    calls = []

    def handler(request):
        calls.append(request)
        return httpx.Response(200, headers={"Content-Encoding": "gzip"},
                              stream=httpx.ByteStream(b"pas du gzip"))

    http = httpx.Client(base_url="http://executor:8100", transport=httpx.MockTransport(handler))
    with pytest.raises(ExecutorUnavailable):
        ExecutorClient(api_key="k", http=http).execute(REQ)
    assert len(calls) == 2


@pytest.mark.parametrize("body", [{"status": "down", "version": "1.0"}, [], "ok"])
def test_health_is_validated(body):
    client, _ = scripted(body)
    with pytest.raises(ExecutorProtocolError):
        client.health()


def test_empty_ticket_id_still_filters():
    client, calls = scripted([])
    client.audit("")
    assert calls[0].url.params.get("ticket_id") == ""


def test_level_out_of_contract_rejected():
    client, _ = scripted(_resp("executed", level=9))
    with pytest.raises(ExecutorProtocolError):
        client.execute(REQ)


def test_base_url_with_v1_suffix():
    assert str(ExecutorClient(base_url="http://executor:8100/v1/")._http.base_url) == "http://executor:8100"


class _Trickle(httpx.SyncByteStream):
    """Serveur qui envoie la réponse octet par octet, lentement."""
    def __iter__(self):
        import time
        for _ in range(40):
            time.sleep(0.05)
            yield b" "


def test_global_deadline_per_attempt():
    import time
    http = httpx.Client(base_url="http://x", transport=httpx.MockTransport(
        lambda request: httpx.Response(200, stream=_Trickle())))
    start = time.monotonic()
    with pytest.raises(ExecutorUnavailable, match="délai"):
        ExecutorClient(api_key="k", timeout_s=0.3, http=http).execute(REQ)
    assert time.monotonic() - start < 1.5              # 2 tentatives × 0,3 s (+ marge)

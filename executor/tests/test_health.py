import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("EXECUTOR_API_KEY", "test-only-executor-key")
    with TestClient(create_app()) as client:
        yield client


def test_health_with_valid_key(client):
    response = client.get(
        "/v1/health", headers={"X-API-Key": "test-only-executor-key"}
    )
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": "1.0"}


@pytest.mark.parametrize("key", [None, "", "wrong-key"])
def test_health_rejects_missing_empty_or_invalid_key(client, key):
    headers = {} if key is None else {"X-API-Key": key}
    response = client.get("/v1/health", headers=headers)
    assert response.status_code == 401
    assert "test-only-executor-key" not in response.text


@pytest.mark.parametrize("configured_key", [None, ""])
def test_unconfigured_secret_never_authorizes(monkeypatch, configured_key):
    if configured_key is None:
        monkeypatch.delenv("EXECUTOR_API_KEY", raising=False)
    else:
        monkeypatch.setenv("EXECUTOR_API_KEY", configured_key)
    with TestClient(create_app()) as client:
        for headers in ({}, {"X-API-Key": ""}, {"X-API-Key": "anything"}):
            assert client.get("/v1/health", headers=headers).status_code == 401


def test_query_parameter_cannot_replace_header(client):
    assert client.get(
        "/v1/health", params={"X-API-Key": "test-only-executor-key"}
    ).status_code == 401


def test_only_contract_health_route_is_exposed(client):
    assert {route.path for route in client.app.routes} == {"/v1/health"}

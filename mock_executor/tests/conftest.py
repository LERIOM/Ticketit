from pathlib import Path
from uuid import uuid4

import pytest
import yaml
from fastapi.testclient import TestClient

from app.main import API_KEY, app
from app.state import STATE

CONTRACT = Path(__file__).resolve().parents[2] / "contracts" / "executor_v1.openapi.yaml"


@pytest.fixture(autouse=True)
def _fresh_lab():
    STATE.reset()
    yield


@pytest.fixture
def client() -> TestClient:
    return TestClient(app, headers={"X-API-Key": API_KEY})


@pytest.fixture(scope="session")
def contract() -> dict:
    return yaml.safe_load(CONTRACT.read_text(encoding="utf-8"))


def exec_body(tool: str, params: dict, confidence: float = 0.9, ticket_id: str = "T-123", **kw) -> dict:
    return {"request_id": kw.get("request_id", str(uuid4())), "ticket_id": ticket_id, "tool": tool,
            "params": params, "confidence": confidence,
            "justification": kw.get("justification", "test")}

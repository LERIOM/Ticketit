"""Le contrat v1 est présent, lisible, et nos modèles en suivent les champs."""
from pathlib import Path

import yaml

from app.models import ExecuteRequest, ExecuteResponse

CONTRACT = Path(__file__).resolve().parents[2] / "contracts" / "executor_v1.openapi.yaml"


def load():
    return yaml.safe_load(CONTRACT.read_text(encoding="utf-8"))


def test_contract_routes():
    paths = set(load()["paths"])
    assert paths == {"/health", "/tools", "/execute", "/approvals/{audit_id}",
                     "/undo/{audit_id}", "/audit"}


def test_contract_status_values():
    assert load()["components"]["schemas"]["Status"]["enum"] == [
        "executed", "refused", "pending_approval", "failed"]


def test_models_cover_contract_fields():
    schemas = load()["components"]["schemas"]
    assert set(schemas["ExecuteRequest"]["required"]) == set(ExecuteRequest.model_fields)
    assert set(schemas["ExecuteResponse"]["required"]) == set(ExecuteResponse.model_fields)

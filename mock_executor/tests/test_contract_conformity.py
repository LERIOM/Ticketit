"""Le mock_executor et contracts/executor_v1.openapi.yaml restent cohérents.

1. Mêmes routes et mêmes méthodes que le contrat.
2. Chaque réponse réelle du mock valide le schéma JSON du contrat.
"""
import copy

import jsonschema
import pytest

from app.main import app

from .conftest import exec_body


def _to_jsonschema(node, components):
    """OpenAPI 3.0 -> JSON Schema : résout les $ref et traduit `nullable`."""
    if isinstance(node, list):
        return [_to_jsonschema(n, components) for n in node]
    if not isinstance(node, dict):
        return node
    if "$ref" in node:
        name = node["$ref"].rsplit("/", 1)[-1]
        return _to_jsonschema(copy.deepcopy(components[name]), components)
    out = {k: _to_jsonschema(v, components) for k, v in node.items() if k not in ("example", "nullable")}
    if node.get("nullable"):
        out = {"anyOf": [out, {"type": "null"}]}
    return out


def schema_of(contract: dict, path: str, method: str) -> dict:
    op = contract["paths"][path][method]
    raw = op["responses"]["200"]["content"]["application/json"]["schema"]
    return _to_jsonschema(raw, contract["components"]["schemas"])


def test_same_routes_and_methods(contract):
    exposed = {}
    for path, item in app.openapi()["paths"].items():
        assert path.startswith("/v1/")
        exposed[path.removeprefix("/v1")] = set(item)
    expected = {p: set(item) for p, item in contract["paths"].items()}
    assert exposed == expected


def test_health_and_tools_match_schema(client, contract):
    jsonschema.validate(client.get("/v1/health").json(), schema_of(contract, "/health", "get"))
    jsonschema.validate(client.get("/v1/tools").json(), schema_of(contract, "/tools", "get"))


@pytest.mark.parametrize("tool,params,conf", [
    ("logs_search", {"query": "203.0.113.5", "since_minutes": 60}, 0.9),   # executed
    ("block_ip", {"ip": "10.0.0.12", "duration_hours": 1}, 0.99),           # pending_approval
    ("delete_data", {"path": "/"}, 0.99),                                   # refused
    ("account_info", {"username": "inconnu"}, 0.9),                         # failed
])
def test_execute_matches_schema(client, contract, tool, params, conf):
    r = client.post("/v1/execute", json=exec_body(tool, params, conf))
    assert r.status_code == 200
    jsonschema.validate(r.json(), schema_of(contract, "/execute", "post"))


def test_approval_undo_audit_match_schema(client, contract):
    pending = client.post("/v1/execute", json=exec_body("isolate_host", {"hostname": "PC-COMPTA-07"})).json()
    approved = client.post(f"/v1/approvals/{pending['audit_id']}",
                           json={"decision": "approve", "approver": "analyste.dupont"}).json()
    jsonschema.validate(approved, schema_of(contract, "/approvals/{audit_id}", "post"))
    undone = client.post(f"/v1/undo/{approved['audit_id']}").json()
    jsonschema.validate(undone, schema_of(contract, "/undo/{audit_id}", "post"))
    entries = client.get("/v1/audit", params={"ticket_id": "T-123"}).json()
    jsonschema.validate(entries, schema_of(contract, "/audit", "get"))
    assert len(entries) == 3


def test_tool_catalog_matches_level_table(client):
    levels = {t["name"]: t["level"] for t in client.get("/v1/tools").json()}
    assert levels == {"logs_search": 0, "account_info": 0, "block_ip": 1,
                      "force_password_reset": 1, "isolate_host": 2, "disable_account": 2}

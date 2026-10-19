import importlib
import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
MOCK_DIR = ROOT / "mock_executor" / "app"


def _load_mock_executor():
    """Charge mock_executor/app sous un autre nom (les deux paquets s'appellent `app`)."""
    name = "mock_executor_app"
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(
            name, MOCK_DIR / "__init__.py", submodule_search_locations=[str(MOCK_DIR)])
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    return importlib.import_module(f"{name}.main"), importlib.import_module(f"{name}.state")


@pytest.fixture
def mock_executor():
    """(TestClient du faux executor, son état). Ignoré si mock_executor/ est absent (image Docker)."""
    if not MOCK_DIR.exists():
        pytest.skip("mock_executor absent")
    from fastapi.testclient import TestClient
    main, state = _load_mock_executor()
    state.STATE.reset()
    return TestClient(main.app), state.STATE

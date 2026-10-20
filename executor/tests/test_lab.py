import json
import sqlite3
import subprocess
import sys

import pytest

from app.lab.seed import events, export_logs, seed
from app.lab.storage import connect, initialize


def snapshot(path):
    with connect(path) as db:
        return {
            table: [tuple(row) for row in db.execute(f"SELECT * FROM {table} ORDER BY 1")]
            for table in ("lab_accounts", "lab_hosts", "lab_blocks", "lab_logs")
        }


def test_seed_reproduces_initial_state_and_preserves_other_tables(tmp_path):
    path = tmp_path / "lab.db"
    seed(path)
    original = snapshot(path)
    with connect(path) as db:
        db.execute("UPDATE lab_accounts SET active = 0")
        db.execute("UPDATE lab_hosts SET isolated = 1")
        db.execute("INSERT INTO lab_blocks VALUES (?, ?)", ("203.0.113.5", "2026-11-04T12:00:00Z"))
        db.execute("CREATE TABLE audit (entry TEXT)")
        db.execute("INSERT INTO audit VALUES ('keep')")
    seed(path)
    assert snapshot(path) == original
    with connect(path) as db:
        assert db.execute("SELECT entry FROM audit").fetchone()[0] == "keep"


def test_initialization_preserves_changes_across_connections(tmp_path):
    path = tmp_path / "lab.db"
    seed(path)
    with connect(path) as db:
        db.execute("UPDATE lab_hosts SET isolated = 1 WHERE hostname = ?", ("DC-01",))
    initialize(path)
    with connect(path) as db:
        assert db.execute("SELECT isolated FROM lab_hosts WHERE hostname = 'DC-01'").fetchone()[0] == 1


def test_transaction_rolls_back_on_failure(tmp_path):
    path = tmp_path / "lab.db"
    seed(path)
    with pytest.raises(sqlite3.IntegrityError):
        with connect(path) as db:
            db.execute("UPDATE lab_accounts SET active = 0")
            db.execute("UPDATE lab_hosts SET isolated = 2")
    with connect(path) as db:
        assert all(row[0] == 1 for row in db.execute("SELECT active FROM lab_accounts"))


def test_seed_failure_does_not_leave_partial_reset(tmp_path):
    path = tmp_path / "lab.db"
    seed(path)
    original = snapshot(path)
    with connect(path) as db:
        db.execute("""CREATE TRIGGER reject_seed BEFORE INSERT ON lab_hosts
                      BEGIN SELECT RAISE(ABORT, 'simulated failure'); END""")
    with pytest.raises(sqlite3.IntegrityError):
        seed(path)
    assert snapshot(path) == original


def test_log_fixtures_are_reproducible_and_match_scenarios(tmp_path):
    path = tmp_path / "lab.db"
    seed(path)
    exported = export_logs(path)
    records = [json.loads(line) for line in exported.splitlines()]
    ssh = [event for event in records if event["scenario"] == "ssh_bruteforce"]
    assert len(ssh) == 12
    assert {event["source_ip"] for event in ssh} == {"203.0.113.5"}
    scan = next(event for event in records if event["scenario"] == "port_scan")
    assert (scan["source_ip"], scan["ports_scanned"], scan["duration_seconds"]) == (
        "198.51.100.23", 300, 30
    )
    assert len(records) == len(events()) == 14
    seed(path)
    assert export_logs(path) == exported


def test_seed_cli_and_export(tmp_path):
    path, logs = tmp_path / "lab.db", tmp_path / "logs.jsonl"
    subprocess.run(
        [sys.executable, "-m", "scripts.seed_lab", "--database", str(path), "--logs", str(logs)],
        check=True, capture_output=True,
    )
    assert logs.read_text(encoding="utf-8") == export_logs(path)


def test_cli_cannot_overwrite_database_with_logs(tmp_path):
    path = tmp_path / "lab.db"
    result = subprocess.run(
        [sys.executable, "-m", "scripts.seed_lab", "--database", str(path), "--logs", str(path)],
        capture_output=True,
    )
    assert result.returncode == 2
    assert not path.exists()

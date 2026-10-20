"""Repeatable demo fixtures, independent from the wall clock."""

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from .storage import connect, initialize

REFERENCE_TIME = datetime(2026, 11, 3, 12, 0, tzinfo=timezone.utc)


def events() -> list[dict]:
    """Internal JSONL fixture format, not the future logs_search API schema."""
    records = []
    for index in range(12):
        records.append({
            "event_id": f"ssh-{index + 1:02}",
            "timestamp": (
                REFERENCE_TIME - timedelta(seconds=120 - index * 10)
            ).isoformat().replace("+00:00", "Z"),
            "scenario": "ssh_bruteforce",
            "source_ip": "203.0.113.5",
            "hostname": "SRV-WEB-01",
            "event": "ssh_authentication_failed",
        })
    records.append({
        "event_id": "scan-01",
        "timestamp": REFERENCE_TIME.isoformat().replace("+00:00", "Z"),
        "scenario": "port_scan",
        "source_ip": "198.51.100.23",
        "hostname": "SRV-WEB-01",
        "event": "port_scan",
        "ports_scanned": 300,
        "duration_seconds": 30,
    })
    records.append({
        "event_id": "phishing-01",
        "timestamp": REFERENCE_TIME.isoformat().replace("+00:00", "Z"),
        "scenario": "phishing_report",
        "username": "j.martin",
        "hostname": "PC-COMPTA-07",
        "event": "credentials_submitted",
    })
    return records


def seed(path: str | Path) -> None:
    """Reset only lab tables atomically; never touch audit/idempotency tables."""
    initialize(path)
    with connect(path) as db:
        for table in ("lab_accounts", "lab_hosts", "lab_blocks", "lab_logs"):
            db.execute(f"DELETE FROM {table}")  # Fixed internal names, not user input.
        db.executemany(
            "INSERT INTO lab_accounts VALUES (?, ?, ?)",
            [(name, 1, 0) for name in ("j.martin", "admin", "svc-backup")],
        )
        db.executemany(
            "INSERT INTO lab_hosts VALUES (?, ?)",
            [(name, 0) for name in ("SRV-WEB-01", "PC-COMPTA-07", "DC-01")],
        )
        db.executemany(
            "INSERT INTO lab_logs VALUES (?, ?, ?)",
            [
                (event["event_id"], event["timestamp"],
                 json.dumps(event, ensure_ascii=False, sort_keys=True))
                for event in events()
            ],
        )


def export_logs(path: str | Path) -> str:
    """Return reproducible JSON Lines from the persisted fixture."""
    with connect(path) as db:
        rows = db.execute(
            "SELECT payload FROM lab_logs ORDER BY timestamp, event_id"
        ).fetchall()
    return "".join(row["payload"] + "\n" for row in rows)

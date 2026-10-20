"""Transactional SQLite storage for the simulated laboratory."""

import sqlite3
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def connect(path: str | Path):
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    try:
        with connection:
            yield connection
    finally:
        connection.close()


def initialize(path: str | Path) -> None:
    """Create missing tables without changing existing laboratory state."""
    with connect(path) as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS lab_accounts (
                username TEXT PRIMARY KEY,
                active INTEGER NOT NULL CHECK (active IN (0, 1)),
                must_change_password INTEGER NOT NULL
                    CHECK (must_change_password IN (0, 1))
            )
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS lab_hosts (
                hostname TEXT PRIMARY KEY,
                isolated INTEGER NOT NULL CHECK (isolated IN (0, 1))
            )
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS lab_blocks (
                ip TEXT PRIMARY KEY,
                blocked_until TEXT NOT NULL
            )
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS lab_logs (
                event_id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                payload TEXT NOT NULL
            )
        """)

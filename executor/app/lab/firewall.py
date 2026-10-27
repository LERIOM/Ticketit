"""Simulated firewall storage, independent from IP authorization policy."""

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from ipaddress import ip_address


def _utc(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("An aware datetime is required")
    return value.astimezone(timezone.utc)


def _text(value: datetime) -> str:
    return _utc(value).isoformat().replace("+00:00", "Z")


def _parse(value: str) -> datetime:
    return _utc(datetime.fromisoformat(value.replace("Z", "+00:00")))


@dataclass(frozen=True)
class BlockChange:
    ip: str
    before: str | None
    after: str


def block_ip(
    db: sqlite3.Connection, ip: str, duration_hours: int, *, now: datetime
) -> BlockChange:
    """Capture the stored preimage, then extend a block without shortening it."""
    if not isinstance(ip, str):
        raise ValueError("IP must be a string")
    address = str(ip_address(ip))
    if type(duration_hours) is not int or not 1 <= duration_hours <= 24:
        raise ValueError("Duration must be an integer from 1 to 24")
    deadline = _utc(now) + timedelta(hours=duration_hours)
    if not db.in_transaction:
        db.execute("BEGIN IMMEDIATE")
    row = db.execute(
        "SELECT blocked_until FROM lab_blocks WHERE ip = ?", (address,)
    ).fetchone()
    before = row[0] if row else None
    if before is not None:
        deadline = max(deadline, _parse(before))
    after = _text(deadline)
    db.execute(
        """INSERT INTO lab_blocks (ip, blocked_until) VALUES (?, ?)
           ON CONFLICT(ip) DO UPDATE SET blocked_until = excluded.blocked_until""",
        (address, after),
    )
    return BlockChange(address, before, after)


def is_blocked(db: sqlite3.Connection, ip: str, *, now: datetime) -> bool:
    """Expiration is evaluated on read; no destructive background cleanup."""
    instant = _utc(now)
    row = db.execute(
        "SELECT blocked_until FROM lab_blocks WHERE ip = ?", (str(ip_address(ip)),)
    ).fetchone()
    return row is not None and _parse(row[0]) > instant

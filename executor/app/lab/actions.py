"""Internal mutations only; callers must authorize before invoking these."""

import sqlite3
from dataclasses import dataclass


class TargetNotFound(LookupError):
    """The requested simulated asset does not exist."""


@dataclass(frozen=True)
class Change:
    target: str
    field: str
    before: bool
    after: bool


def _set_flag(
    db: sqlite3.Connection,
    table: str,
    key: str,
    field: str,
    target: str,
    value: bool,
) -> Change:
    # Identifiers are fixed by the three wrappers, never supplied by an API.
    # Start a write transaction before reading: another writer must not change
    # the preimage between this SELECT and UPDATE.
    if not db.in_transaction:
        db.execute("BEGIN IMMEDIATE")
    row = db.execute(
        f"SELECT {field} FROM {table} WHERE {key} = ?", (target,)
    ).fetchone()
    if row is None:
        raise TargetNotFound(target)
    before = bool(row[0])
    db.execute(
        f"UPDATE {table} SET {field} = ? WHERE {key} = ?",
        (int(value), target),
    )
    # The caller owns commit/rollback, allowing future audit and idempotency
    # writes to be part of the very same transaction.
    return Change(target, field, before, value)


def force_password_reset(db: sqlite3.Connection, username: str) -> Change:
    return _set_flag(
        db, "lab_accounts", "username", "must_change_password", username, True
    )


def disable_account(db: sqlite3.Connection, username: str) -> Change:
    return _set_flag(db, "lab_accounts", "username", "active", username, False)


def isolate_host(db: sqlite3.Connection, hostname: str) -> Change:
    return _set_flag(db, "lab_hosts", "hostname", "isolated", hostname, True)

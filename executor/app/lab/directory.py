"""Read simulated account state, without inventing protection policy."""

import sqlite3
from dataclasses import dataclass

from .actions import TargetNotFound


@dataclass(frozen=True)
class AccountState:
    username: str
    active: bool
    must_change_password: bool


def read_account(db: sqlite3.Connection, username: str) -> AccountState:
    row = db.execute(
        "SELECT username, active, must_change_password FROM lab_accounts WHERE username = ?",
        (username,),
    ).fetchone()
    if row is None:
        raise TargetNotFound(username)
    return AccountState(row[0], bool(row[1]), bool(row[2]))

import pytest

from app.lab.actions import (
    TargetNotFound,
    disable_account,
    force_password_reset,
    isolate_host,
)
from app.lab.seed import seed
from app.lab.storage import connect


CASES = [
    (force_password_reset, "j.martin", "lab_accounts", "username", "must_change_password", False, True),
    (disable_account, "j.martin", "lab_accounts", "username", "active", True, False),
    (isolate_host, "PC-COMPTA-07", "lab_hosts", "hostname", "isolated", False, True),
]


@pytest.fixture
def database(tmp_path):
    path = tmp_path / "lab.db"
    seed(path)
    return path


@pytest.mark.parametrize("action,target,table,key,field,before,after", CASES)
def test_action_persists_and_captures_previous_state(
    database, action, target, table, key, field, before, after
):
    with connect(database) as db:
        change = action(db, target)
        assert (change.target, change.field, change.before, change.after) == (
            target, field, before, after
        )
    with connect(database) as db:
        assert bool(db.execute(
            f"SELECT {field} FROM {table} WHERE {key} = ?", (target,)
        ).fetchone()[0]) is after
        repeated = action(db, target)
        assert repeated.before is after
        assert repeated.after is after


@pytest.mark.parametrize("action,target,table,key,field,before,after", CASES)
def test_action_rolls_back_with_later_failure(
    database, action, target, table, key, field, before, after
):
    with pytest.raises(RuntimeError):
        with connect(database) as db:
            action(db, target)
            raise RuntimeError("simulated later audit write failure")
    with connect(database) as db:
        assert bool(db.execute(
            f"SELECT {field} FROM {table} WHERE {key} = ?", (target,)
        ).fetchone()[0]) is before


@pytest.mark.parametrize("action", [force_password_reset, disable_account, isolate_host])
@pytest.mark.parametrize("target", ["unknown", "admin'; DROP TABLE lab_accounts; --"])
def test_missing_or_sql_like_target_does_not_mutate(database, action, target):
    with pytest.raises(TargetNotFound):
        with connect(database) as db:
            action(db, target)
    with connect(database) as db:
        assert [tuple(row) for row in db.execute(
            "SELECT active, must_change_password FROM lab_accounts"
        )] == [(1, 0)] * 3
        assert [row[0] for row in db.execute("SELECT isolated FROM lab_hosts")] == [0] * 3


def test_actions_share_callers_transaction(database):
    with pytest.raises(RuntimeError):
        with connect(database) as db:
            db.execute("BEGIN IMMEDIATE")
            disable_account(db, "j.martin")
            isolate_host(db, "PC-COMPTA-07")
            raise RuntimeError("rollback whole operation")
    with connect(database) as db:
        assert db.execute(
            "SELECT active FROM lab_accounts WHERE username = 'j.martin'"
        ).fetchone()[0] == 1
        assert db.execute(
            "SELECT isolated FROM lab_hosts WHERE hostname = 'PC-COMPTA-07'"
        ).fetchone()[0] == 0

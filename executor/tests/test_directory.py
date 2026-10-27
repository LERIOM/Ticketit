import pytest

from app.lab.actions import TargetNotFound, disable_account, force_password_reset
from app.lab.directory import read_account
from app.lab.seed import seed
from app.lab.storage import connect


def test_read_account_reflects_persisted_changes(tmp_path):
    path = tmp_path / "lab.db"
    seed(path)
    with connect(path) as db:
        original = read_account(db, "j.martin")
        assert original.active is True
        assert original.must_change_password is False
        disable_account(db, "j.martin")
        force_password_reset(db, "j.martin")
    with connect(path) as db:
        changed = read_account(db, "j.martin")
        assert changed.active is False
        assert changed.must_change_password is True
        assert read_account(db, "admin").active is True
        with pytest.raises(TargetNotFound):
            read_account(db, "' OR 1=1 --")

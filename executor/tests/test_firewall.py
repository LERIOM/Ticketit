from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from threading import Barrier

import pytest

from app.lab.firewall import block_ip, is_blocked
from app.lab.seed import seed
from app.lab.storage import connect

NOW = datetime(2026, 11, 3, 12, tzinfo=timezone.utc)
IP = "203.0.113.5"


@pytest.fixture
def database(tmp_path):
    path = tmp_path / "lab.db"
    seed(path)
    return path


def test_block_expiration_and_preimage(database):
    with connect(database) as db:
        change = block_ip(db, IP, 1, now=NOW)
        assert change.before is None
        assert change.after == "2026-11-03T13:00:00Z"
    with connect(database) as db:
        assert is_blocked(db, IP, now=NOW)
        assert not is_blocked(db, IP, now=NOW + timedelta(hours=1))
        assert not is_blocked(db, "198.51.100.23", now=NOW)
        renewed = block_ip(db, IP, 1, now=NOW + timedelta(hours=2))
        assert renewed.before == change.after
        assert renewed.after == "2026-11-03T15:00:00Z"


def test_existing_block_never_shortened(database):
    with connect(database) as db:
        first = block_ip(db, IP, 24, now=NOW)
        second = block_ip(db, IP, 1, now=NOW)
        assert second.before == second.after == first.after


def test_rollback(database):
    with pytest.raises(RuntimeError):
        with connect(database) as db:
            block_ip(db, IP, 1, now=NOW)
            raise RuntimeError("later audit failure")
    with connect(database) as db:
        assert not is_blocked(db, IP, now=NOW)


@pytest.mark.parametrize("duration", [0, 25, True, 1.5, "1"])
def test_invalid_duration_does_not_write(database, duration):
    with connect(database) as db:
        with pytest.raises(ValueError):
            block_ip(db, IP, duration, now=NOW)
        assert db.execute("SELECT COUNT(*) FROM lab_blocks").fetchone()[0] == 0


@pytest.mark.parametrize("ip", ["0.0.0.0/0", "bad'; DROP TABLE lab_blocks; --", 123])
def test_invalid_address_does_not_write(database, ip):
    with connect(database) as db:
        with pytest.raises(ValueError):
            block_ip(db, ip, 1, now=NOW)
        assert db.execute("SELECT COUNT(*) FROM lab_blocks").fetchone()[0] == 0


def test_clock_must_be_aware(database):
    with connect(database) as db:
        with pytest.raises(ValueError):
            block_ip(db, IP, 1, now=NOW.replace(tzinfo=None))
        assert not db.in_transaction


def test_ipv6_equivalent_spellings_share_one_block(database):
    with connect(database) as db:
        first = block_ip(db, "2001:db8:0:0:0:0:0:1", 24, now=NOW)
        second = block_ip(db, "2001:db8::1", 1, now=NOW)
        assert first.ip == second.ip == "2001:db8::1"
        assert second.before == second.after == first.after
        assert db.execute("SELECT COUNT(*) FROM lab_blocks").fetchone()[0] == 1


def test_offset_clock_is_stored_in_utc(database):
    with connect(database) as db:
        local_now = NOW.astimezone(timezone(timedelta(hours=2)))
        assert block_ip(db, IP, 1, now=local_now).after == "2026-11-03T13:00:00Z"


def test_simultaneous_extensions_are_serialized(database):
    barrier = Barrier(2)

    def write(duration):
        with connect(database) as db:
            barrier.wait(timeout=5)
            return block_ip(db, IP, duration, now=NOW)

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(write, [1, 24]))
    first = next(result for result in results if result.before is None)
    second = next(result for result in results if result.before is not None)
    assert second.before == first.after
    with connect(database) as db:
        assert db.execute("SELECT blocked_until FROM lab_blocks").fetchone()[0] == (
            "2026-11-04T12:00:00Z"
        )

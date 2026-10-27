"""Table de pseudonymes chiffrée et stockage SQLite."""
import sqlite3

from cryptography.fernet import Fernet

from app.models import Source, Ticket
from app.security.vault import Vault
from app.store import Store

MAPPING = {"<PERSONNE_1>": "Jean Dupont", "<TEL_1>": "06 12 34 56 78"}


def test_seal_open_roundtrip():
    v = Vault(Fernet.generate_key().decode())
    token = v.seal(MAPPING)
    assert "Jean" not in token and v.open(token) == MAPPING


def test_wrong_key_gives_empty_mapping_not_crash():
    token = Vault(Fernet.generate_key().decode()).seal(MAPPING)
    assert Vault(Fernet.generate_key().decode()).open(token) == {}


def test_missing_key_uses_ephemeral_key():
    v = Vault(None)
    assert v.open(v.seal(MAPPING)) == MAPPING


def test_store_keeps_mapping_encrypted_at_rest(tmp_path):
    db = tmp_path / "t.db"
    store = Store(db, Vault(Fernet.generate_key().decode()))
    t = store.save_ticket(Ticket(source=Source.USER, text_masked="Appelez <PERSONNE_1> au <TEL_1>."))
    store.save_mapping(t.id, MAPPING)
    assert store.get_mapping(t.id) == MAPPING
    assert store.get_ticket(t.id).text_masked == t.text_masked
    raw = " ".join(str(c) for row in sqlite3.connect(db).execute(
        "SELECT * FROM docs UNION ALL SELECT ticket_id, sealed, '', '' FROM pseudonyms") for c in row)
    assert "Jean Dupont" not in raw and "06 12 34 56 78" not in raw


def test_unknown_ticket_has_empty_mapping(tmp_path):
    assert Store(tmp_path / "t.db", Vault(None)).get_mapping("T-inconnu") == {}

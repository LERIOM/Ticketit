"""Stockage local SQLite : documents JSON par collection + table de pseudonymes chiffrée.

Collections : `tickets` (modèle Ticket), puis `candidates` (boucle d'apprentissage).
"""
import json
import sqlite3
import threading
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any

from .config import settings
from .models import Ticket, TicketStatus
from .security.vault import Vault


class Store:
    def __init__(self, path: Path | str, vault: Vault) -> None:
        if str(path) != ":memory:":
            Path(path).parent.mkdir(parents=True, exist_ok=True)
        self._db = sqlite3.connect(str(path), check_same_thread=False)
        self._lock = threading.Lock()
        self._vault = vault
        with self._lock, self._db:
            self._db.execute("""CREATE TABLE IF NOT EXISTS docs (
                collection TEXT NOT NULL, id TEXT NOT NULL, data TEXT NOT NULL,
                updated_at TEXT NOT NULL, PRIMARY KEY (collection, id))""")
            self._db.execute("""CREATE TABLE IF NOT EXISTS pseudonyms (
                ticket_id TEXT PRIMARY KEY, sealed TEXT NOT NULL)""")

    # ------------------------------------------------------------ documents
    def put(self, collection: str, doc_id: str, data: dict[str, Any]) -> None:
        now = datetime.now(timezone.utc).isoformat()
        with self._lock, self._db:
            self._db.execute("INSERT OR REPLACE INTO docs VALUES (?, ?, ?, ?)",
                             (collection, doc_id, json.dumps(data, ensure_ascii=False, default=str), now))

    def get(self, collection: str, doc_id: str) -> dict[str, Any] | None:
        with self._lock:
            row = self._db.execute("SELECT data FROM docs WHERE collection=? AND id=?",
                                   (collection, doc_id)).fetchone()
        return json.loads(row[0]) if row else None

    def all(self, collection: str) -> list[dict[str, Any]]:
        with self._lock:
            rows = self._db.execute("SELECT data FROM docs WHERE collection=? ORDER BY updated_at DESC",
                                    (collection,)).fetchall()
        return [json.loads(r[0]) for r in rows]

    # -------------------------------------------------------------- tickets
    def save_ticket(self, ticket: Ticket) -> Ticket:
        self.put("tickets", ticket.id, ticket.model_dump(mode="json"))
        return ticket

    def get_ticket(self, ticket_id: str) -> Ticket | None:
        data = self.get("tickets", ticket_id)
        return Ticket.model_validate(data) if data else None

    def list_tickets(self, status: TicketStatus | None = None) -> list[Ticket]:
        tickets = [Ticket.model_validate(d) for d in self.all("tickets")]
        return [t for t in tickets if status is None or t.status == status]

    # ----------------------------------------------------------- pseudonymes
    def save_mapping(self, ticket_id: str, mapping: dict[str, str]) -> None:
        with self._lock, self._db:
            self._db.execute("INSERT OR REPLACE INTO pseudonyms VALUES (?, ?)",
                             (ticket_id, self._vault.seal(mapping)))

    def get_mapping(self, ticket_id: str) -> dict[str, str]:
        with self._lock:
            row = self._db.execute("SELECT sealed FROM pseudonyms WHERE ticket_id=?",
                                   (ticket_id,)).fetchone()
        return self._vault.open(row[0]) if row else {}


@lru_cache(maxsize=1)
def get_store() -> Store:
    return Store(settings.data_dir / "engine.db", Vault(settings.vault_key))

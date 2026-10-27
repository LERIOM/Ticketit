"""Table de correspondance pseudonyme -> valeur, chiffrée (Fernet) côté serveur.

Clé : variable VAULT_KEY (générer avec
`python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`).
Sans clé, une clé éphémère est générée : les correspondances sont perdues au redémarrage.
"""
import json
import logging

from cryptography.fernet import Fernet, InvalidToken

log = logging.getLogger(__name__)


class Vault:
    def __init__(self, key: str | None) -> None:
        if not key:
            log.warning("VAULT_KEY absente : clé éphémère, pseudonymes perdus au redémarrage")
            key = Fernet.generate_key().decode()
        self._fernet = Fernet(key.encode())

    def seal(self, mapping: dict[str, str]) -> str:
        return self._fernet.encrypt(json.dumps(mapping, ensure_ascii=False).encode()).decode()

    def open(self, token: str) -> dict[str, str]:
        try:
            return json.loads(self._fernet.decrypt(token.encode()))
        except InvalidToken:
            log.error("table de pseudonymes illisible (VAULT_KEY changée ?)")
            return {}

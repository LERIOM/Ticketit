"""Configuration lue dans l'environnement (.env)."""
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

# dépôt : <racine>/engine/app/config.py -> <racine>/data ; Docker : /srv/app -> /data (volume)
_DATA = Path(__file__).resolve().parents[2] / "data"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    executor_url: str = "http://localhost:8100"
    executor_api_key: str = "change-me"
    executor_timeout_s: float = 5.0

    llm_provider: Literal["ollama", "api"] = "ollama"
    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:7b-instruct"
    ollama_embed_model: str = "bge-m3"
    llm_timeout_s: float = 120.0
    # API commerciale optionnelle (ne reçoit que du texte masqué)
    api_model: str = "claude-opus-5-5"
    anthropic_api_key: str | None = None

    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "change-me-neo4j"
    retriever: Literal["neo4j", "memory"] = "neo4j"

    decision_confidence_threshold: float = 0.75

    # Stockage local : tickets + table de pseudonymes chiffrée
    data_dir: Path = _DATA / "runtime"
    kb_dir: Path = _DATA / "kb"
    vault_key: str | None = None          # clé Fernet ; générée (éphémère) si absente

    spacy_model_fr: str = "fr_core_news_md"
    spacy_model_en: str = "en_core_web_md"
    injection_threshold: float = 0.7


settings = Settings()

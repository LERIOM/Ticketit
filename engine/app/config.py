"""Configuration lue dans l'environnement (.env)."""
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    executor_url: str = "http://localhost:8100"
    executor_api_key: str = "change-me"
    executor_timeout_s: float = 5.0

    llm_provider: Literal["ollama", "api"] = "ollama"
    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:7b-instruct"

    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "change-me-neo4j"

    decision_confidence_threshold: float = 0.75


settings = Settings()

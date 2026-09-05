"""Configuration de l'application, chargée depuis les variables d'environnement.

Aucun secret n'a de valeur par défaut : leur absence doit faire échouer le
démarrage plutôt que de faire tourner l'API avec une clé faible connue de tous.
"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "SHEQ Management API"
    app_version: str = "0.1.0"
    environment: str = "development"

    database_url: str = "sqlite:///./sheq.db"

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 15
    jwt_refresh_token_expire_days: int = 7

    fernet_master_key: str

    cors_origins: list[str] = ["http://localhost:5173"]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

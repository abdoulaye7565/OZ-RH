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

    # Stockage des pièces jointes (photos, sauvegardes) : hors base de données,
    # système de fichiers local pour le MVP (point 9 du CDC — pas de dépendance
    # à un stockage objet tant que le volume ne le justifie pas).
    storage_dir: str = "./storage"

    # Notifications (prompt 4.4, section 6.3 du CDC). Aucun serveur SMTP n'est
    # imposé par le CDC : configuration optionnelle (None = envoi de courriels
    # non tenté, journalisé comme tel — pas une erreur silencieuse, un choix
    # explicite de configuration absente).
    smtp_hote: str | None = None
    smtp_port: int = 587
    smtp_utilisateur: str | None = None
    smtp_mot_de_passe: str | None = None
    smtp_expediteur: str = "notifications@hirondelles-it-lab.local"

    # Désactive le planificateur de tâches (APScheduler) : mis à False dans
    # tests/conftest.py pour qu'aucune tâche planifiée ne s'exécute pendant les
    # tests (ils utiliseraient une session/BD différente de celle du planificateur,
    # qui ouvre toujours sa propre session sur la base réelle).
    scheduler_actif: bool = True


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

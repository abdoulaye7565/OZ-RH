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

    # Sauvegarde automatique de la base (revue d'ensemble 2026-09-10 — contrainte
    # §2 traçabilité / §4 secrets hors sauvegarde). Le script Scripts/sauvegarde.py
    # existait mais n'était planifié nulle part. Job quotidien via APScheduler ;
    # `sauvegarde_active=False` le désactive (ex. si une sauvegarde externe
    # d'infrastructure prend déjà le relais).
    sauvegarde_active: bool = True
    sauvegarde_dir: str = "./sauvegardes"
    sauvegarde_heure: int = 2  # 2 h du matin, hors heures d'activité
    sauvegarde_retention: int = 14  # nb d'archives conservées (les plus anciennes sont supprimées)

    # Service d'assistance IA (lot 6, chapitre 16 du CDC — prompt 6.1, socle
    # technique seul, aucune fonction métier). Interrupteur général désactivé
    # par défaut : "le mode dégradé est la norme" (tableau 10) tant qu'aucune
    # fonction n'est validée pour un usage réel. Fournisseur retenu : Anthropic
    # (décision explicite, hors CDC qui n'impose aucun fournisseur).
    assistance_activee: bool = False
    assistance_api_cle: str | None = None
    assistance_modele: str = "claude-haiku-4-5-20251001"
    assistance_delai_max_secondes: float = 10.0
    # None = pas de plafond configuré (aucune alerte, aucune désactivation
    # automatique) — un déploiement de test peut vouloir garder le socle actif
    # sans encore avoir arbitré de budget avec la direction (16.6).
    assistance_plafond_mensuel_usd: float | None = None

    # Assistant documentaire (prompt 6.2, chapitre 16.2.1/16.3.2 du CDC) —
    # première fonction du lot 6, son propre indicateur d'activation (voir
    # app/services/assistance/configuration.py). Fournisseur d'embeddings
    # distinct d'Anthropic (retenu au prompt 6.1) : Anthropic n'expose aucune
    # API de représentation vectorielle publique — Voyage AI est le
    # partenaire qu'Anthropic recommande elle-même pour cet usage (décision
    # explicite avec l'utilisateur, prompt 6.2).
    assistance_assistant_documentaire_active: bool = False
    assistance_voyage_api_cle: str | None = None
    assistance_modele_embeddings: str = "voyage-3-lite"

    # Pré-rédaction des rapports (prompt 6.4, chapitre 16.2.4) : réutilise
    # entièrement le client Anthropic du prompt 6.1, aucun nouveau fournisseur.
    assistance_pre_redaction_active: bool = False


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

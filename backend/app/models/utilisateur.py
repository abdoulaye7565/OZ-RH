"""Entité UTILISATEUR — CDC chapitre 7.2.1. Toute personne disposant d'un accès
à l'application."""
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import BaseModel, enum_column
from app.models.enums import RoleUtilisateur


class Utilisateur(BaseModel):
    __tablename__ = "utilisateur"

    nom: Mapped[str] = mapped_column(String(60), nullable=False)
    prenom: Mapped[str] = mapped_column(String(60), nullable=False)
    identifiant: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    mot_de_passe: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[RoleUtilisateur] = mapped_column(enum_column(RoleUtilisateur, "role_utilisateur"), nullable=False)
    site_id: Mapped[int | None] = mapped_column(ForeignKey("site.id"), nullable=True)
    courriel: Mapped[str | None] = mapped_column(String(120), nullable=True)
    # Photo de profil (2026-09-10, retour direct de l'utilisateur — "insérer
    # sa photo lors de la connexion", compris comme un ajout en libre-service
    # une fois connecté : aucune photo ne peut raisonnablement se rattacher à
    # un compte avant que l'identifiant/mot de passe ne l'aient authentifié).
    # Chemin relatif sous storage_dir, comme les autres pièces jointes — même
    # convention que Signalement.photos, Document.fichier.
    photo: Mapped[str | None] = mapped_column(String(255), nullable=True)
    actif: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    derniere_connexion: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    # Protection contre le brute-force sur /auth/connexion (revue de sécurité
    # du 2026-09-08, CLAUDE.md point 10) : jamais exposés par UtilisateurSortie
    # (schemas/auth.py, liste explicite de champs) — état interne uniquement.
    tentatives_echouees: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    verrouille_jusqua: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

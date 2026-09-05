"""Entité UTILISATEUR — CDC chapitre 7.2.1. Toute personne disposant d'un accès
à l'application."""
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String
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
    actif: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    derniere_connexion: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

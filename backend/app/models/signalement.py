"""Entité SIGNALEMENT — CDC chapitre 7.2.3."""
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import BaseModel, enum_column
from app.models.enums import StatutSignalement, TypeSignalement


class Signalement(BaseModel):
    __tablename__ = "signalement"

    # Attribuée à la synchronisation, pas à la saisie (CLAUDE.md règle 7) : nullable
    # tant que le signalement n'a pas encore été synchronisé.
    reference: Mapped[str | None] = mapped_column(String(20), unique=True, nullable=True)
    type: Mapped[TypeSignalement] = mapped_column(enum_column(TypeSignalement, "type_signalement"), nullable=False)
    site_id: Mapped[int] = mapped_column(ForeignKey("site.id"), nullable=False)
    lieu: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    # Liste de chemins de fichiers ; les fichiers eux-mêmes vivent hors base (point 3
    # de CLAUDE.md, exigence non fonctionnelle "pièces jointes").
    photos: Mapped[list | None] = mapped_column(JSON, nullable=True)
    anonyme: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    # Vide si anonyme=True, y compris en base et dans les journaux (règle 3, CLAUDE.md).
    auteur_id: Mapped[int | None] = mapped_column(ForeignKey("utilisateur.id"), nullable=True)
    date_constat: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    date_saisie: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    date_synchro: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    causes: Mapped[str | None] = mapped_column(Text, nullable=True)
    risque_id: Mapped[int | None] = mapped_column(ForeignKey("risque.id"), nullable=True)
    statut: Mapped[StatutSignalement] = mapped_column(
        enum_column(StatutSignalement, "statut_signalement"),
        default=StatutSignalement.NOUVEAU,
        nullable=False,
    )

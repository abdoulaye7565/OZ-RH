"""Entité SEANCE — hors dictionnaire, séance de sensibilisation/formation
(section 5.3.3, FOR-SHEQ-014 « Feuille de présence »)."""
from datetime import date

from sqlalchemy import Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import BaseModel, enum_column
from app.models.enums import StatutSeance


class Seance(BaseModel):
    __tablename__ = "seance"

    theme: Mapped[str] = mapped_column(String(200), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    lieu: Mapped[str] = mapped_column(String(120), nullable=False)
    animateur_id: Mapped[int] = mapped_column(ForeignKey("utilisateur.id"), nullable=False)
    # Facultatif : une séance rattachée à une compétence renouvelle
    # automatiquement l'habilitation des participants présents à sa clôture
    # (service métier) — cohérent avec les "données gérées" de la section
    # 5.3.3, qui lient explicitement compétences et séances.
    competence_id: Mapped[int | None] = mapped_column(ForeignKey("competence.id"), nullable=True)
    statut: Mapped[StatutSeance] = mapped_column(
        enum_column(StatutSeance, "statut_seance"), default=StatutSeance.PLANIFIEE, nullable=False
    )

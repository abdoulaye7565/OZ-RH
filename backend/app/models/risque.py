"""Entité RISQUE — CDC chapitre 7.2.2."""
from datetime import date

from sqlalchemy import CheckConstraint, Date, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import BaseModel, enum_column
from app.models.enums import CategorieRisque, NiveauRisque


class Risque(BaseModel):
    __tablename__ = "risque"
    __table_args__ = (
        CheckConstraint("probabilite BETWEEN 1 AND 5", name="ck_risque_probabilite_1_5"),
        CheckConstraint("gravite BETWEEN 1 AND 5", name="ck_risque_gravite_1_5"),
    )

    numero: Mapped[int] = mapped_column(Integer, nullable=False)
    danger: Mapped[str] = mapped_column(String(200), nullable=False)
    categorie: Mapped[CategorieRisque] = mapped_column(
        enum_column(CategorieRisque, "categorie_risque"), nullable=False
    )
    unite_travail: Mapped[str] = mapped_column(String(80), nullable=False)
    personnes_exposees: Mapped[str | None] = mapped_column(String(120), nullable=True)
    mesures_existantes: Mapped[str | None] = mapped_column(Text, nullable=True)
    probabilite: Mapped[int] = mapped_column(Integer, nullable=False)
    gravite: Mapped[int] = mapped_column(Integer, nullable=False)
    # Calculés (règle 6, CLAUDE.md) : renseignés par le service métier à l'écriture,
    # pas par une colonne générée en base, pour rester lisibles par SQLite ET PostgreSQL.
    criticite: Mapped[int] = mapped_column(Integer, nullable=False)
    niveau: Mapped[NiveauRisque] = mapped_column(enum_column(NiveauRisque, "niveau_risque"), nullable=False)
    mesures_proposees: Mapped[str] = mapped_column(Text, nullable=False)
    date_evaluation: Mapped[date] = mapped_column(Date, nullable=False)
    auteur_id: Mapped[int] = mapped_column(ForeignKey("utilisateur.id"), nullable=False)

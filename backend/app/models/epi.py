"""Entité EPI — CDC chapitre 7.2.6. Équipement de protection individuelle antichute
suivi individuellement. Un EPI réformé ne peut jamais être réactivé (règle métier
à faire respecter au niveau service, lot 2 — pas une contrainte exprimable en SQL
portable simple)."""
from datetime import date

from sqlalchemy import Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import BaseModel, enum_column
from app.models.enums import StatutEpi, TypeEpi


class Epi(BaseModel):
    __tablename__ = "epi"

    numero: Mapped[str] = mapped_column(String(12), unique=True, nullable=False)
    type: Mapped[TypeEpi] = mapped_column(enum_column(TypeEpi, "type_epi"), nullable=False)
    marque_modele: Mapped[str] = mapped_column(String(80), nullable=False)
    date_fabrication: Mapped[date | None] = mapped_column(Date, nullable=True)
    date_mise_service: Mapped[date] = mapped_column(Date, nullable=False)
    date_limite: Mapped[date] = mapped_column(Date, nullable=False)
    porteur_id: Mapped[int | None] = mapped_column(ForeignKey("utilisateur.id"), nullable=True)
    derniere_verification: Mapped[date | None] = mapped_column(Date, nullable=True)
    # Calculé (règle 6, CLAUDE.md) : dernière vérification + 12 mois.
    prochaine_verification: Mapped[date | None] = mapped_column(Date, nullable=True)
    statut: Mapped[StatutEpi] = mapped_column(
        enum_column(StatutEpi, "statut_epi"), default=StatutEpi.EN_SERVICE, nullable=False
    )

"""Entité CAMPAGNE_AUDIT — hors dictionnaire (section 5.3.4)."""
from datetime import date

from sqlalchemy import Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import BaseModel, enum_column
from app.models.enums import StatutInspection

# StatutInspection (en_cours/cloturee) réutilisé tel quel : même cycle de vie
# qu'une inspection (cotation en cours, puis clôture), pas de raison d'inventer
# un énuméré distinct pour un besoin identique.


class CampagneAudit(BaseModel):
    __tablename__ = "campagne_audit"

    # Nullable : généré paresseusement au premier export PDF (prompt 5.1).
    reference: Mapped[str | None] = mapped_column(String(20), unique=True, nullable=True)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    auditeur_id: Mapped[int] = mapped_column(ForeignKey("utilisateur.id"), nullable=False)
    statut: Mapped[StatutInspection] = mapped_column(
        enum_column(StatutInspection, "statut_inspection"), default=StatutInspection.EN_COURS, nullable=False
    )

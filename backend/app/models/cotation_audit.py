"""Entité COTATION_AUDIT — hors dictionnaire, une ligne par (campagne, exigence)
cotée (section 5.3.4 : "cotant chaque exigence de zéro à deux"). Cotation 0/1/2
définie par FOR-SHEQ-017 : 0 = absent, 1 = partiel, 2 = conforme."""
from sqlalchemy import CheckConstraint, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import BaseModel


class CotationAudit(BaseModel):
    __tablename__ = "cotation_audit"
    __table_args__ = (CheckConstraint("cotation BETWEEN 0 AND 2", name="cotation_0_2"),)

    campagne_id: Mapped[int] = mapped_column(ForeignKey("campagne_audit.id"), nullable=False)
    exigence_id: Mapped[int] = mapped_column(ForeignKey("exigence_audit.id"), nullable=False)
    cotation: Mapped[int] = mapped_column(Integer, nullable=False)
    constat: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Pertinent seulement si cotation < 2 ; sert de base à la création d'une
    # action corrective (section 5.3.4 : "Créer une action corrective à partir
    # d'un écart").
    ecart: Mapped[str | None] = mapped_column(Text, nullable=True)

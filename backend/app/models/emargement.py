"""Entité EMARGEMENT — hors dictionnaire, présence à une séance (section 5.3.3 :
"Émarger une présence depuis un mobile ou une tablette", FOR-SHEQ-014)."""
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import BaseModel


class Emargement(BaseModel):
    __tablename__ = "emargement"

    seance_id: Mapped[int] = mapped_column(ForeignKey("seance.id"), nullable=False)
    participant_id: Mapped[int] = mapped_column(ForeignKey("utilisateur.id"), nullable=False)
    present: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    signe_le: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

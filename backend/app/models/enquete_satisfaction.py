"""Entité ENQUETE_SATISFACTION — hors dictionnaire, section 5.3.6 combinée,
FOR-SHEQ-018 « Fiche de satisfaction client ». Envoyée par lien public sans
compte (5.3.6 : "Envoyer une enquête de satisfaction par lien ou code") : le
jeton est la seule protection d'accès à la réponse, pas d'authentification."""
import secrets
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import BaseModel


def _generer_jeton() -> str:
    return secrets.token_urlsafe(24)


class EnqueteSatisfaction(BaseModel):
    __tablename__ = "enquete_satisfaction"

    jeton: Mapped[str] = mapped_column(String(40), unique=True, nullable=False, default=_generer_jeton)
    client: Mapped[str] = mapped_column(String(120), nullable=False)
    site_id: Mapped[int | None] = mapped_column(ForeignKey("site.id"), nullable=True)
    intervention: Mapped[str] = mapped_column(String(200), nullable=False)
    technicien_id: Mapped[int | None] = mapped_column(ForeignKey("utilisateur.id"), nullable=True)
    envoyee_le: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    # Usage unique : une fois répondue, le jeton ne rouvre plus le
    # questionnaire (règle de service — voir satisfaction_service.py).
    repondu: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

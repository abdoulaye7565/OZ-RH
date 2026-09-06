"""Entité TENTATIVE_QUIZ — hors dictionnaire, résultat d'un passage de quiz
(section 5.3.3 : "Répondre à un quiz et obtenir son score immédiatement")."""
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import BaseModel


class TentativeQuiz(BaseModel):
    __tablename__ = "tentative_quiz"

    seance_id: Mapped[int] = mapped_column(ForeignKey("seance.id"), nullable=False)
    participant_id: Mapped[int] = mapped_column(ForeignKey("utilisateur.id"), nullable=False)
    # Liste de {"question_id": int, "reponse": "a"} — jamais le score fourni
    # par le client : recalculé côté serveur à partir de ces réponses (règle 6,
    # CLAUDE.md — jamais de valeur métier calculée acceptée telle quelle).
    reponses: Mapped[list] = mapped_column(JSON, nullable=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    # Instantané du nombre de questions au moment du passage : si le
    # référentiel évolue plus tard (question ajoutée/archivée), un score déjà
    # obtenu ne doit jamais être réinterprété différemment.
    total_questions: Mapped[int] = mapped_column(Integer, nullable=False)
    reussi: Mapped[bool] = mapped_column(Boolean, nullable=False)
    date_passation: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

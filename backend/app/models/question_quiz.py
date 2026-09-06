"""Entité QUESTION_QUIZ — hors dictionnaire, référentiel paramétrable du quiz
d'évaluation (section 5.3.3, FOR-SHEQ-015 « Quiz d'évaluation post-sensibilisation »),
même principe que POINT_CHECKLIST : géré par le référent SHEQ, jamais une
constante Python figée dans le code."""
from sqlalchemy import JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import BaseModel


class QuestionQuiz(BaseModel):
    __tablename__ = "question_quiz"

    enonce: Mapped[str] = mapped_column(Text, nullable=False)
    # Liste de {"lettre": "a", "texte": "..."} — 2 ou 3 choix selon la question
    # réelle (FOR-SHEQ-015), pas un nombre fixe.
    choix: Mapped[list] = mapped_column(JSON, nullable=False)
    reponse_correcte: Mapped[str] = mapped_column(String(1), nullable=False)

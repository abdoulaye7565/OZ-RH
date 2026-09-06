"""Entité DECISION_REVUE — hors dictionnaire (section 5.3.4 : "Enregistrer les
décisions de la revue et en suivre la réalisation" ; "les décisions de revue
non soldées sont automatiquement reportées en données d'entrée de la revue
suivante"). Le report est géré par le service métier (une décision ouverte de
n'importe quelle revue passée apparaît dans les données d'entrée de la
suivante) : `revue_id` reste celui de la revue qui l'a créée, jamais réécrit —
cohérent avec le principe de ne jamais modifier un enregistrement historique
pour en déplacer l'appartenance."""
from datetime import date

from sqlalchemy import Date, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import BaseModel, enum_column
from app.models.enums import StatutDecisionRevue


class DecisionRevue(BaseModel):
    __tablename__ = "decision_revue"

    revue_id: Mapped[int] = mapped_column(ForeignKey("revue_direction.id"), nullable=False)
    libelle: Mapped[str] = mapped_column(Text, nullable=False)
    responsable_id: Mapped[int] = mapped_column(ForeignKey("utilisateur.id"), nullable=False)
    echeance: Mapped[date] = mapped_column(Date, nullable=False)
    statut: Mapped[StatutDecisionRevue] = mapped_column(
        enum_column(StatutDecisionRevue, "statut_decision_revue"),
        default=StatutDecisionRevue.OUVERTE,
        nullable=False,
    )

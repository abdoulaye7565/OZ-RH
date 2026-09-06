"""Entité REVUE_DIRECTION — hors dictionnaire (section 5.3.4, FOR-SHEQ-016
« Compte rendu de revue de direction SHEQ »)."""
from datetime import date

from sqlalchemy import JSON, Date, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import BaseModel


class RevueDirection(BaseModel):
    __tablename__ = "revue_direction"

    date: Mapped[date] = mapped_column(Date, nullable=False)
    lieu: Mapped[str | None] = mapped_column(String(120), nullable=True)
    redacteur_id: Mapped[int] = mapped_column(ForeignKey("utilisateur.id"), nullable=False)
    periode_debut: Mapped[date] = mapped_column(Date, nullable=False)
    periode_fin: Mapped[date] = mapped_column(Date, nullable=False)
    # Texte libre : le formulaire réel ("Participants (direction, référent
    # SHEQ, représentants du personnel)") ne demande pas de liste structurée
    # d'utilisateurs, juste une mention des présents.
    participants: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Instantané assemblé à la création (règle 5.2.5 : "rapport pré-alimenté
    # par les données de la période") : jamais recalculé après coup, un
    # rapport de revue ne doit pas changer rétroactivement si les données
    # sources évoluent ensuite.
    donnees_entree: Mapped[dict] = mapped_column(JSON, nullable=False)

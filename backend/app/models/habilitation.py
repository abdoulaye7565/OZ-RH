"""Entité HABILITATION — hors dictionnaire, cellule de la « matrice de
compétences » (section 5.3.3) : une ligne par (collaborateur, compétence)
obtenue, avec sa date d'expiration. Plusieurs lignes peuvent exister pour le
même couple au fil des recyclages successifs — la plus récente fait foi,
même principe que l'historique des cotations de risque (prompt 4.1) : on ne
réécrit jamais une ligne existante pour la "renouveler"."""
from datetime import date

from sqlalchemy import Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import BaseModel


class Habilitation(BaseModel):
    __tablename__ = "habilitation"

    utilisateur_id: Mapped[int] = mapped_column(ForeignKey("utilisateur.id"), nullable=False)
    competence_id: Mapped[int] = mapped_column(ForeignKey("competence.id"), nullable=False)
    date_obtention: Mapped[date] = mapped_column(Date, nullable=False)
    # Amorcée à l'obtention (date_obtention + périodicité de la compétence) —
    # même principe que Epi.prochaine_verification (prompt 2.1).
    date_expiration: Mapped[date] = mapped_column(Date, nullable=False)

    @property
    def expiree(self) -> bool:
        """Calculé (règle 6, CLAUDE.md) : jamais stocké. Règle 5.3.3 : "Une
        compétence expirée est signalée dans la matrice"."""
        return self.date_expiration < date.today()

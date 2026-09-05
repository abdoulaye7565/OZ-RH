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
    # Absent du dictionnaire (7.2.6) mais nécessaire : sans ce champ, le motif de
    # réforme (ex. "a arrêté une chute") saisi à l'appel de l'API serait accepté
    # puis silencieusement perdu — ajouté pour ne pas mentir sur ce qui est
    # réellement conservé (prompt 2.1).
    motif_reforme: Mapped[str | None] = mapped_column(String(300), nullable=True)

    @property
    def est_conforme(self) -> bool:
        """Calculé (chapitre 7.3.2 du CDC) : seul le statut EN_SERVICE est
        conforme — À_VERIFIER, RETIRÉ et RÉFORMÉ ne le sont jamais. La date de
        prochaine vérification est vérifiée en plus, indépendamment du statut
        stocké : sans tâche planifiée qui resynchronise `statut` chaque nuit
        (absente tant que le lot 4.4 n'existe pas), un EPI resté EN_SERVICE en
        base après l'échéance ne doit pas être compté conforme pour autant.
        Utilisé par la règle de blocage des permis (lot 2.2)."""
        if self.statut != StatutEpi.EN_SERVICE:
            return False
        if self.prochaine_verification is not None and self.prochaine_verification < date.today():
            return False
        return True

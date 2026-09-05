"""Entité JOURNAL_ACCES — CDC chapitre 7.2.8. Écriture seule (règle 4, CLAUDE.md) :
n'hérite volontairement PAS de BaseModel, qui porte modifie_le/modifie_par_id et
archive — trois colonnes qui suggéreraient, à tort, qu'une entrée peut être modifiée
ou archivée. Seules id/cree_le/cree_par_id/organisation_id ont un sens ici ;
cree_par_id fait doublon avec utilisateur_id mais vient de la classe de base commune
demandée par CLAUDE.md : conservé pour l'uniformité, sans usage prévu.
"""
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, enum_column
from app.models.enums import ActionJournal


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class JournalAcces(Base):
    __tablename__ = "journal_acces"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cree_le: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, nullable=False)
    cree_par_id: Mapped[int | None] = mapped_column(ForeignKey("utilisateur.id", use_alter=True), nullable=True)
    organisation_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    secret_id: Mapped[int] = mapped_column(ForeignKey("secret.id"), nullable=False)
    utilisateur_id: Mapped[int] = mapped_column(ForeignKey("utilisateur.id"), nullable=False)
    horodatage: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, nullable=False)
    action: Mapped[ActionJournal] = mapped_column(enum_column(ActionJournal, "action_journal"), nullable=False)

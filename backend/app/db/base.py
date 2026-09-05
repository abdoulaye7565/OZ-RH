"""Déclaration de base SQLAlchemy et classe de base commune à toutes les entités métier.

La classe de base commune porte les colonnes exigées par CLAUDE.md (point 5) :
id, cree_le, cree_par_id, modifie_le, modifie_par_id, archive, organisation_id.

Nommage : le cahier des charges (chapitre 7) nomme chaque clé primaire
`id_<entite>` (ex. id_utilisateur). Le prompt de modélisation demande explicitement
une classe de base commune portant une colonne `id` unique — cette exigence
transversale prime sur le nommage par entité du dictionnaire. Voir docs/JOURNAL.md
pour le détail de cet arbitrage.
"""
import enum
from datetime import datetime, timezone
from typing import TypeVar

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, MetaData
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

E = TypeVar("E", bound=enum.Enum)


def enum_column(enum_cls: type[E], name: str) -> SAEnum:
    """Colonne énumérée stockant la *valeur* Python (ex. "MikroTik") plutôt que le
    nom du membre (ex. "MIKROTIK"), pour rester lisible directement en base."""
    return SAEnum(enum_cls, name=name, values_callable=lambda cls: [e.value for e in cls])


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


# Convention de nommage explicite : requise pour que `use_alter=True` (ci-dessous)
# puisse générer un nom de contrainte déterministe à chaque table concrète.
NAMING_CONVENTION = {
    "ix": "ix_%(table_name)s_%(column_0_name)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)


class BaseModel(Base):
    """Classe abstraite : toutes les tables métier en héritent.

    `organisation_id` prépare le multi-entreprises (CLAUDE.md point 5) mais n'est
    pas exploité en v1 : pas de clé étrangère tant qu'aucune table ORGANISATION
    n'existe, valeur non utilisée pour l'instant.
    """

    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cree_le: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, nullable=False)
    # use_alter=True : UTILISATEUR et SITE se référencent mutuellement (site_id sur
    # UTILISATEUR, cree_par_id/modifie_par_id vers UTILISATEUR sur toutes les tables
    # y compris SITE). Ce cycle est réel et bloquerait la création des tables sur
    # PostgreSQL sans ce report de contrainte à une étape ALTER TABLE séparée.
    cree_par_id: Mapped[int | None] = mapped_column(
        ForeignKey("utilisateur.id", use_alter=True), nullable=True
    )
    modifie_le: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow, nullable=False
    )
    modifie_par_id: Mapped[int | None] = mapped_column(
        ForeignKey("utilisateur.id", use_alter=True), nullable=True
    )
    archive: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    organisation_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

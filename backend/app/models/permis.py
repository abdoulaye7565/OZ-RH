"""Entité PERMIS — CDC chapitre 7.2.7. Le champ "intervenants" est de type Liste au
dictionnaire : modélisé ici par une véritable table d'association (many-to-many)
plutôt qu'une liste JSON d'identifiants, pour garantir l'intégrité référentielle
(un intervenant supprimé/archivé ne doit pas laisser un identifiant orphelin)."""
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, ForeignKey, JSON, Numeric, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, BaseModel, enum_column
from app.models.enums import StatutPermis, SupportPermis

if TYPE_CHECKING:
    from app.models.utilisateur import Utilisateur

permis_intervenants = Table(
    "permis_intervenants",
    Base.metadata,
    Column("permis_id", ForeignKey("permis.id"), primary_key=True),
    Column("utilisateur_id", ForeignKey("utilisateur.id"), primary_key=True),
)


class Permis(BaseModel):
    __tablename__ = "permis"

    reference: Mapped[str | None] = mapped_column(String(16), unique=True, nullable=True)
    site_id: Mapped[int] = mapped_column(ForeignKey("site.id"), nullable=False)
    nature_travaux: Mapped[str] = mapped_column(String(200), nullable=False)
    support: Mapped[SupportPermis] = mapped_column(enum_column(SupportPermis, "support_permis"), nullable=False)
    hauteur_estimee: Mapped[float | None] = mapped_column(Numeric(4, 1), nullable=True)
    intervenants: Mapped[list["Utilisateur"]] = relationship("Utilisateur", secondary=permis_intervenants)
    surveillant_id: Mapped[int] = mapped_column(ForeignKey("utilisateur.id"), nullable=False)
    debut_validite: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    fin_validite: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    # Résultat des vérifications automatiques (règle 1, CLAUDE.md) : calculé par le
    # service de délivrance (lot 2), pas saisi.
    controles: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    statut: Mapped[StatutPermis] = mapped_column(
        enum_column(StatutPermis, "statut_permis"), default=StatutPermis.DEMANDE, nullable=False
    )
    validateur_id: Mapped[int | None] = mapped_column(ForeignKey("utilisateur.id"), nullable=True)

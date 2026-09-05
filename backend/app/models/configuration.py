"""Entité CONFIGURATION — CDC chapitre 7.2.5. Immuable après création (règle 5,
CLAUDE.md) : cette contrainte est une règle de service (aucune route de
modification/suppression exposée), pas une contrainte SQL — voir prompt 3.2."""
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import BaseModel, enum_column
from app.models.enums import TypeIntervention


class Configuration(BaseModel):
    __tablename__ = "configuration"

    reference: Mapped[str] = mapped_column(String(24), unique=True, nullable=False)
    equipement_id: Mapped[int] = mapped_column(ForeignKey("equipement.id"), nullable=False)
    type_intervention: Mapped[TypeIntervention] = mapped_column(
        enum_column(TypeIntervention, "type_intervention"), nullable=False
    )
    version_logicielle: Mapped[str | None] = mapped_column(String(40), nullable=True)
    # Champs "Structure" du dictionnaire : structure libre, modélisée en JSON comme
    # le fait implicitement le dictionnaire lui-même pour ces champs composites.
    parametres_reseau: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    parametres_sansfil: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    signal_dbm: Mapped[float | None] = mapped_column(Numeric(5, 1), nullable=True)
    ccq_pourcent: Mapped[int | None] = mapped_column(Integer, nullable=True)
    tests_realises: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    # Chemins de fichiers ; nommage SITE-IDENTITY-AAAAMMJJ contrôlé côté service.
    fichiers_sauvegarde: Mapped[list | None] = mapped_column(JSON, nullable=True)
    technicien_id: Mapped[int] = mapped_column(ForeignKey("utilisateur.id"), nullable=False)
    date_intervention: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

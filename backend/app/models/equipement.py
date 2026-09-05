"""Entité EQUIPEMENT — CDC chapitre 7.2.4."""
from datetime import date

from sqlalchemy import Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import BaseModel, enum_column
from app.models.enums import MarqueEquipement, StatutEquipement


class Equipement(BaseModel):
    __tablename__ = "equipement"

    identity: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    marque: Mapped[MarqueEquipement] = mapped_column(enum_column(MarqueEquipement, "marque_equipement"), nullable=False)
    modele: Mapped[str] = mapped_column(String(60), nullable=False)
    numero_serie: Mapped[str] = mapped_column(String(60), unique=True, nullable=False)
    adresse_mac: Mapped[str | None] = mapped_column(String(17), nullable=True)
    site_id: Mapped[int] = mapped_column(ForeignKey("site.id"), nullable=False)
    emplacement: Mapped[str] = mapped_column(String(120), nullable=False)
    date_installation: Mapped[date] = mapped_column(Date, nullable=False)
    fin_garantie: Mapped[date | None] = mapped_column(Date, nullable=True)
    statut: Mapped[StatutEquipement] = mapped_column(
        enum_column(StatutEquipement, "statut_equipement"), default=StatutEquipement.EN_SERVICE, nullable=False
    )

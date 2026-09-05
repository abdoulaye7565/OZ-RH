"""Entité SITE — non détaillée par le dictionnaire du CDC (chapitre 7.2), reconstituée
depuis le MCD (docs/diagrammes/mcd.png) et la section 5.2.3. Représente un lieu
(siège ou site client) auquel se rattachent utilisateurs, équipements et permis."""
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import BaseModel, enum_column
from app.models.enums import TypeSite


class Site(BaseModel):
    __tablename__ = "site"

    nom: Mapped[str] = mapped_column(String(120), nullable=False)
    type: Mapped[TypeSite] = mapped_column(enum_column(TypeSite, "type_site"), nullable=False)
    adresse: Mapped[str | None] = mapped_column(String(200), nullable=True)

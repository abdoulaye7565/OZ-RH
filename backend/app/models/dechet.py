"""Entité DECHET — hors dictionnaire, section 5.3.6 combinée, REG-SHEQ-005
« Registre de gestion des déchets » (attention particulière aux DEEE et
batteries, mais le registre réel n'est pas limité aux seuls DEEE)."""
from datetime import date

from sqlalchemy import Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import BaseModel


class Dechet(BaseModel):
    __tablename__ = "dechet"

    date: Mapped[date] = mapped_column(Date, nullable=False)
    # Texte libre (pas un énuméré) : le registre réel n'impose pas de liste
    # fermée ("DEEE" en est l'exemple donné, mais pas la seule valeur possible).
    type: Mapped[str] = mapped_column(String(60), nullable=False)
    description: Mapped[str] = mapped_column(String(200), nullable=False)
    # Texte libre également : le registre réel mélange unités ("2 unités",
    # "kg") plutôt qu'un nombre et une unité séparés — fidèle à la donnée
    # source plutôt qu'une structure plus stricte non demandée.
    quantite: Mapped[str] = mapped_column(String(60), nullable=False)
    site_id: Mapped[int] = mapped_column(ForeignKey("site.id"), nullable=False)
    filiere: Mapped[str] = mapped_column(String(120), nullable=False)
    date_enlevement: Mapped[date | None] = mapped_column(Date, nullable=True)
    justificatif: Mapped[str | None] = mapped_column(String(255), nullable=True)

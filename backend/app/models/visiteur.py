"""Entité VISITEUR — hors dictionnaire (chapitre 7 : aucune entité pour ce
module), section 5.3.6 combinée (Visiteurs, déchets et satisfaction client),
REG-SHEQ-004 « Registre des visiteurs »."""
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import BaseModel


class Visiteur(BaseModel):
    __tablename__ = "visiteur"

    nom: Mapped[str] = mapped_column(String(120), nullable=False)
    societe: Mapped[str | None] = mapped_column(String(120), nullable=True)
    motif: Mapped[str] = mapped_column(String(200), nullable=False)
    # Texte libre plutôt qu'une clé étrangère vers UTILISATEUR : le registre
    # réel (REG-SHEQ-004) note un nom en clair, pas nécessairement celui d'un
    # compte de l'application (accueil, service générique, etc.).
    personne_visitee: Mapped[str | None] = mapped_column(String(120), nullable=True)
    heure_arrivee: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    heure_depart: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    # Règle 5.3.6 : "un visiteur ne peut être enregistré sans validation de la
    # lecture des consignes de sécurité" — vérifié par le service à la
    # création (règle de service, pas seulement une valeur par défaut).
    consignes_lues: Mapped[bool] = mapped_column(Boolean, nullable=False)

    @property
    def present(self) -> bool:
        """Calculé (règle 6, CLAUDE.md) : un visiteur est "présent" tant
        qu'aucune heure de départ n'est enregistrée — sert de base à la liste
        d'évacuation (section 5.3.6)."""
        return self.heure_depart is None

"""Entité DOCUMENT — non détaillée par le dictionnaire (chapitre 7.2), reconstituée
depuis le MCD et la section 5.3.5.

Une nouvelle version (PRO-SHEQ-004, § 3 "RÉVISION : toute modification crée une
nouvelle version (01 → 02) ; l'ancienne est déplacée en 09-Archives et n'est
plus utilisée") est une NOUVELLE ligne, jamais une réécriture de l'ancienne —
même principe que CONFIGURATION et COTATION_RISQUE. `reference` n'est donc
plus unique à elle seule : c'est le couple (reference, version) qui l'est ;
la règle "une seule version en vigueur à la fois" (5.3.5) est une règle de
service, pas une contrainte SQL (comme le reste du cycle de vie)."""
from datetime import date

from sqlalchemy import CheckConstraint, Date, ForeignKey, Integer, JSON, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import BaseModel, enum_column
from app.models.enums import ConfidentialiteDocument, StatutDocument


class Document(BaseModel):
    __tablename__ = "document"
    __table_args__ = (
        CheckConstraint("niveau BETWEEN 1 AND 4", name="ck_document_niveau_1_4"),
        UniqueConstraint("reference", "version", name="uq_document_reference_version"),
    )

    reference: Mapped[str] = mapped_column(String(30), nullable=False)
    intitule: Mapped[str] = mapped_column(String(200), nullable=False)
    # Reprend la hiérarchie à 4 niveaux du SMI documentaire existant (politique,
    # pilotage, procédures, formulaires). Colonne entière : NiveauDocument (IntEnum)
    # sert de garde-fou côté Python/Pydantic, pas de type énuméré SQL (SQLAlchemy
    # Enum attend des chaînes, pas des entiers).
    niveau: Mapped[int] = mapped_column(Integer, nullable=False)
    version: Mapped[str] = mapped_column(String(10), nullable=False)
    redacteur_id: Mapped[int] = mapped_column(ForeignKey("utilisateur.id"), nullable=False)
    approbateur_id: Mapped[int | None] = mapped_column(ForeignKey("utilisateur.id"), nullable=True)
    statut: Mapped[StatutDocument] = mapped_column(
        enum_column(StatutDocument, "statut_document"), default=StatutDocument.BROUILLON, nullable=False
    )
    date_revue: Mapped[date | None] = mapped_column(Date, nullable=True)
    confidentialite: Mapped[ConfidentialiteDocument] = mapped_column(
        enum_column(ConfidentialiteDocument, "confidentialite_document"),
        default=ConfidentialiteDocument.NORMAL,
        nullable=False,
    )
    fichier: Mapped[str | None] = mapped_column(String(255), nullable=True)
    # Liste de {utilisateur_id, date} : pas d'entité ACCUSE_LECTURE parmi les 14
    # demandées ; à revoir en table dédiée si le volume de lecteurs le justifie.
    accuses_lecture: Mapped[list | None] = mapped_column(JSON, nullable=True)

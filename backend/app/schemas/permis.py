"""Schémas Pydantic du module Permis (prompt 2.2, section 5.2.2 du CDC)."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from app.models.enums import StatutPermis, SupportPermis


class PermisCreation(BaseModel):
    site_id: int
    nature_travaux: str
    support: SupportPermis
    hauteur_estimee: float | None = None
    intervenant_ids: list[int]
    surveillant_id: int | None = None
    debut_validite: datetime
    fin_validite: datetime

    @field_validator("intervenant_ids")
    @classmethod
    def _au_moins_un_intervenant(cls, v: list[int]) -> list[int]:
        if not v:
            raise ValueError("Au moins un intervenant est requis")
        return v

    @model_validator(mode="after")
    def _meme_journee(self) -> "PermisCreation":
        # Règle 5.2.2 : "Un permis est valable pour une journée et un chantier ;
        # tout changement impose un nouveau permis."
        if self.fin_validite <= self.debut_validite:
            raise ValueError("La fin du créneau doit être postérieure au début")
        if self.debut_validite.date() != self.fin_validite.date():
            raise ValueError("Un permis ne peut couvrir qu'une seule journée")
        return self


class RefusEntree(BaseModel):
    motif: str


class ControlesAutomatiquesSortie(BaseModel):
    conforme: bool
    motifs: list[str]


class PermisSortie(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    reference: str | None
    site_id: int
    nature_travaux: str
    support: SupportPermis
    hauteur_estimee: float | None
    surveillant_id: int | None
    debut_validite: datetime
    fin_validite: datetime
    controles: dict | None
    statut: StatutPermis
    validateur_id: int | None
    archive: bool
    cree_le: datetime
    cree_par_id: int | None
    modifie_le: datetime
    modifie_par_id: int | None
    intervenant_ids: list[int] = []

    @model_validator(mode="before")
    @classmethod
    def _extraire_intervenant_ids(cls, obj):
        # `intervenants` est une relation ORM (liste d'objets Utilisateur) ; la
        # sortie API n'expose que les identifiants, pas les profils complets
        # (déjà accessibles via /auth/utilisateurs si besoin).
        if hasattr(obj, "intervenants"):
            return {
                **{c.name: getattr(obj, c.name) for c in obj.__table__.columns},
                "intervenant_ids": [u.id for u in obj.intervenants],
            }
        return obj

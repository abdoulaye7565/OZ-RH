"""Schémas Pydantic du module Permis (prompt 2.2, section 5.2.2 du CDC)."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from app.models.enums import DecisionSlam, StatutPermis, SupportPermis


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


class EvaluationSlamLiee(BaseModel):
    """Évaluation SLAM rattachée à un permis (revue d'ensemble 2026-09-10) —
    montrée sur l'écran de validation pour que le responsable voie
    concrètement quelle SLAM justifie l'intervention de chaque personne."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    reference: str | None
    utilisateur_id: int
    utilisateur_nom: str | None = None
    decision: DecisionSlam
    date: datetime
    motif: str | None


class ControleDetail(BaseModel):
    cle: str
    libelle: str
    conforme: bool
    detail: str | None = None


class ControlesAutomatiquesSortie(BaseModel):
    conforme: bool
    motifs: list[str]
    # Ajouté au prompt 2.3 (rétrocompatible, `motifs` conservé) : l'écran de
    # validation responsable doit afficher les QUATRE conditions avec leur
    # résultat individuel ("liste des contrôles automatiques avec leur
    # résultat"), pas seulement les motifs des conditions en échec.
    details: list[ControleDetail] = []


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
    # Évaluations SLAM rattachées (revue d'ensemble 2026-09-10). Vide tant
    # qu'aucune n'a été rapprochée (aucun intervenant n'a de SLAM le jour du
    # créneau) — c'est alors la ligne de contrôle « slam » de `controles.details`
    # qui porte le blocage.
    evaluations_slam: list[EvaluationSlamLiee] = []

    @model_validator(mode="before")
    @classmethod
    def _extraire_relations(cls, obj):
        # `intervenants` / `evaluations_slam` sont des relations ORM ; la sortie
        # API n'expose que ce qui est utile aux écrans (identifiants
        # d'intervenants ; SLAM avec nom résolu).
        if hasattr(obj, "intervenants"):
            evaluations = []
            for ev in getattr(obj, "evaluations_slam", []):
                u = ev.utilisateur
                evaluations.append(
                    {
                        "id": ev.id,
                        "reference": ev.reference,
                        "utilisateur_id": ev.utilisateur_id,
                        "utilisateur_nom": f"{u.prenom} {u.nom}" if u else None,
                        "decision": ev.decision,
                        "date": ev.date,
                        "motif": ev.motif,
                    }
                )
            return {
                **{c.name: getattr(obj, c.name) for c in obj.__table__.columns},
                "intervenant_ids": [u.id for u in obj.intervenants],
                "evaluations_slam": evaluations,
            }
        return obj

"""Schémas Pydantic du tableau de bord (prompt 1.5, section 5.4 du CDC).

Étendu le 2026-09-08 : les quatre familles d'indicateurs prévues par la
section 5.4 ("sécurité et santé, prévention, environnement et qualité,
suivi des échéances") ne pouvaient être calculées qu'à partir des seuls
modules Signalements/Actions au moment du prompt 1.5 — EPI, Inspections,
Formations, Documents et Satisfaction sont désormais construits (chantier
"construire tous les écrans", 2026-09-07) et alimentent chacun un indicateur
réel ici. Seuls les incidents environnementaux et la sécurité des données
(coffre-fort) restent sans module source — voir `modules_non_disponibles`.
"""
from datetime import date, datetime

from pydantic import BaseModel

from app.schemas.action import SyntheseActions
from app.schemas.signalement import SignalementSortie


class SignalementParMois(BaseModel):
    annee: int
    mois: int
    nombre: int


class SignalementsResume(BaseModel):
    total_periode: int
    par_mois: list[SignalementParMois]
    nombre_a_traiter: int
    a_traiter: list[SignalementSortie]


class SecuriteResume(BaseModel):
    """Famille "sécurité et santé" (5.4) : accidents et presque-accidents
    tels qu'enregistrés par TypeSignalement — la distinction "avec/sans
    arrêt" et le décompte des jours d'arrêt, cités par le CDC, ne sont pas
    dans le dictionnaire de données du signalement (aucun champ ne les
    porte) : non simulés, seul le décompte réellement saisi est présenté."""

    accidents_periode: int
    presque_accidents_periode: int
    jours_sans_accident: int | None  # None si aucun accident n'a jamais été enregistré


class InspectionsResume(BaseModel):
    realisees_periode: int
    taux_conformite_moyen: float | None  # fraction 0-1, cohérent avec Inspection.taux_conformite


class EpiResume(BaseModel):
    a_verifier_bientot: int  # échéance dans l'horizon, pas encore dépassée
    verifications_depassees: int


class FormationsResume(BaseModel):
    seances_a_venir: int
    personnel_forme: int
    personnel_total: int


class DocumentsResume(BaseModel):
    a_reviser_bientot: int
    en_attente_approbation: int


class SatisfactionResume(BaseModel):
    reclamations_periode: int  # réponses avec note ≤ 2 (nécessite_analyse) reçues sur la période
    note_moyenne: float | None  # sur 5


class EcheanceSortie(BaseModel):
    """Échéance unifiée (5.4, "suivi des échéances") — actions, vérifications
    d'EPI, documents à réviser et séances de sensibilisation à venir,
    fusionnés en une seule liste triée par proximité, comme le montre la
    maquette (#p-dash, "Échéances proches")."""

    type: str  # "action" | "epi" | "document" | "formation"
    reference: str | None
    libelle: str
    echeance: date


class Periode(BaseModel):
    debut: datetime | None
    fin: datetime | None


class TableauBordSortie(BaseModel):
    periode: Periode
    site_id: int | None
    signalements: SignalementsResume
    securite: SecuriteResume
    actions: SyntheseActions
    inspections: InspectionsResume
    epi: EpiResume
    formations: FormationsResume
    documents: DocumentsResume
    satisfaction: SatisfactionResume
    echeances_proches: list[EcheanceSortie]
    # Familles d'indicateurs prévues au chapitre 5.4 du CDC sans module source
    # (incidents environnementaux, sécurité des données/coffre-fort — celui-ci
    # bloqué depuis le prompt 3.3, en attente de validation). Listées plutôt
    # que simulées par une valeur inventée — "aucune donnée saisie
    # manuellement" s'applique aussi à "aucune donnée fabriquée".
    modules_non_disponibles: list[str]

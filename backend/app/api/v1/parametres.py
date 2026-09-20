"""Écran Paramètres (revue d'ensemble 2026-09-10 — retour direct de
l'utilisateur : « le système n'affiche pas tous les modules dans la barre
latérale »). La maquette prévoit un écran Paramètres (`id="p-param"`),
jamais construit jusqu'ici — c'est le module manquant.

Volontairement en LECTURE SEULE pour l'instant : les seuils métier
(criticité 4/8/15, vérification EPI 12 mois...) sont des règles appliquées
côté serveur (CLAUDE.md règle 6, jamais « seulement côté interface » —
règle 7 CLAUDE.md) — les rendre modifiables en base serait un changement de
portée sur des règles de sécurité, à traiter explicitement, pas glissé dans
cet écran. Ce que cet écran EXPOSE reste vrai : comptages réels des
référentiels, état réel de la sauvegarde automatique (lot 2026-09-10)."""
import json
from pathlib import Path

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.deps import require_role
from app.core.permissions import Permissions
from app.db.session import get_db
from app.models.competence import Competence
from app.models.dechet import Dechet
from app.models.enums import CategorieRisque, TypeInspection
from app.models.equipement import Equipement
from app.models.risque import Risque
from app.models.site import Site
from app.models.utilisateur import Utilisateur
from app.services.sauvegarde_service import _PREFIXE

router = APIRouter(prefix="/parametres", tags=["parametres"])


class ReferentielsSortie(BaseModel):
    sites: int
    equipements: int
    categories_risque_utilisees: int
    categories_risque_total: int
    types_dechets: int
    modeles_checklist: int
    competences_formation: int


class DerniereSauvegardeSortie(BaseModel):
    horodatage_utc: str | None = None
    type_base: str | None = None


class SauvegardeSortie(BaseModel):
    active: bool
    heure: int
    retention: int
    nombre_archives: int
    derniere: DerniereSauvegardeSortie | None = None


class ParametresSortie(BaseModel):
    referentiels: ReferentielsSortie
    sauvegarde: SauvegardeSortie


def _etat_sauvegarde() -> SauvegardeSortie:
    dossier = Path(settings.sauvegarde_dir)
    archives = (
        sorted((p for p in dossier.glob(f"{_PREFIXE}*") if p.is_dir()), key=lambda p: p.name)
        if dossier.exists()
        else []
    )
    derniere = None
    if archives:
        manifeste_chemin = archives[-1] / "manifeste.json"
        if manifeste_chemin.exists():
            try:
                manifeste = json.loads(manifeste_chemin.read_text(encoding="utf-8"))
                derniere = DerniereSauvegardeSortie(
                    horodatage_utc=manifeste.get("horodatage_utc"), type_base=manifeste.get("type_base")
                )
            except (json.JSONDecodeError, OSError):
                derniere = None
    return SauvegardeSortie(
        active=settings.sauvegarde_active,
        heure=settings.sauvegarde_heure,
        retention=settings.sauvegarde_retention,
        nombre_archives=len(archives),
        derniere=derniere,
    )


@router.get("", response_model=ParametresSortie)
def obtenir_parametres(
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(require_role(*Permissions.GERER_UTILISATEURS)),
) -> ParametresSortie:
    """Vue d'ensemble des référentiels réels et de l'état de la sauvegarde
    automatique. Réservé à l'administrateur (même périmètre que la gestion
    des utilisateurs — écran de configuration système)."""
    categories_utilisees = db.scalar(select(func.count(func.distinct(Risque.categorie))))
    types_dechets_utilises = db.scalar(select(func.count(func.distinct(Dechet.type))))

    referentiels = ReferentielsSortie(
        sites=db.scalar(select(func.count()).select_from(Site).where(Site.archive.is_(False))) or 0,
        equipements=db.scalar(select(func.count()).select_from(Equipement).where(Equipement.archive.is_(False))) or 0,
        categories_risque_utilisees=categories_utilisees or 0,
        categories_risque_total=len(CategorieRisque),
        types_dechets=types_dechets_utilises or 0,
        modeles_checklist=len(TypeInspection),
        competences_formation=db.scalar(
            select(func.count()).select_from(Competence).where(Competence.archive.is_(False))
        )
        or 0,
    )

    return ParametresSortie(referentiels=referentiels, sauvegarde=_etat_sauvegarde())

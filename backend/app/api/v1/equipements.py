"""Routes du module Parc d'équipements (prompt 3.1, section 5.2.3 du CDC)."""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_role
from app.core.permissions import Permissions
from app.db.session import get_db
from app.models.enums import MarqueEquipement
from app.models.equipement import Equipement
from app.models.utilisateur import Utilisateur
from app.schemas.equipement import (
    EquipementCreation,
    EquipementMiseAJour,
    EquipementSortie,
    FicheEquipementSortie,
    RapportImport,
)
from app.services.equipement_service import (
    creer_equipement,
    mettre_a_jour_equipement,
    obtenir_fiche,
    rechercher_equipements,
)
from app.services.import_parc_service import importer_parc

router = APIRouter(prefix="/equipements", tags=["equipements"])

# Taille bornée pour un import de référentiel (pas un flux illimité) : cohérent
# avec la limite déjà posée sur les photos (app/core/fichiers.py).
TAILLE_MAX_IMPORT_OCTETS = 5 * 1024 * 1024


def _recuperer(db: Session, equipement_id: int) -> Equipement:
    equipement = db.get(Equipement, equipement_id)
    if equipement is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Équipement introuvable")
    return equipement


@router.post("", response_model=EquipementSortie, status_code=status.HTTP_201_CREATED)
def creer(
    payload: EquipementCreation,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(require_role(*Permissions.GERER_PARC)),
) -> Equipement:
    """Ajoute un équipement au parc."""
    return creer_equipement(db, payload, cree_par_id=utilisateur.id)


@router.get("", response_model=list[EquipementSortie])
def lister(
    identity: str | None = None,
    site_id: int | None = None,
    numero_serie: str | None = None,
    marque: MarqueEquipement | None = None,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_current_user),
) -> list[Equipement]:
    """Recherche les équipements du parc, avec filtres optionnels par IDENTITY,
    site, numéro de série et marque."""
    return rechercher_equipements(db, identity=identity, site_id=site_id, numero_serie=numero_serie, marque=marque)


@router.get("/{equipement_id}", response_model=EquipementSortie)
def lire(
    equipement_id: int,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_current_user),
) -> Equipement:
    """Récupère un équipement par son identifiant."""
    return _recuperer(db, equipement_id)


@router.get("/{equipement_id}/fiche", response_model=FicheEquipementSortie)
def fiche(
    equipement_id: int,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_current_user),
) -> dict:
    """Renvoie la fiche complète d'un équipement (historique des configurations et
    interventions associées)."""
    equipement = _recuperer(db, equipement_id)
    return obtenir_fiche(db, equipement)


@router.patch("/{equipement_id}", response_model=EquipementSortie)
def modifier(
    equipement_id: int,
    payload: EquipementMiseAJour,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(require_role(*Permissions.GERER_PARC)),
) -> Equipement:
    """Met à jour les informations d'un équipement du parc."""
    equipement = _recuperer(db, equipement_id)
    return mettre_a_jour_equipement(db, equipement, payload, modifie_par_id=utilisateur.id)


@router.post("/import", response_model=RapportImport)
async def importer(
    fichier: UploadFile,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(require_role(*Permissions.IMPORTER_PARC)),
) -> RapportImport:
    """Importe en masse un référentiel d'équipements depuis un fichier (5 Mo
    maximum) et renvoie un rapport ligne par ligne des créations et rejets."""
    contenu = await fichier.read()
    if len(contenu) > TAILLE_MAX_IMPORT_OCTETS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Fichier trop volumineux : {len(contenu) / 1024 / 1024:.1f} Mo (5 Mo maximum)",
        )
    return importer_parc(db, contenu, fichier.filename or "", cree_par_id=utilisateur.id)

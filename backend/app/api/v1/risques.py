"""Routes du module Risques (prompt 4.1, section 5.2.5 du CDC)."""
from datetime import date

from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_role
from app.core.permissions import Permissions
from app.db.session import get_db
from app.models.enums import CategorieRisque, NiveauRisque
from app.models.utilisateur import Utilisateur
from app.schemas.risque import (
    CelluleMatrice,
    CotationEntree,
    CotationSortie,
    RapportImportRisques,
    RevueDueSortie,
    RisqueCreation,
    RisqueDetailSortie,
    RisqueSortie,
)
from app.services.import_risques_service import importer_registre
from app.services.risque_service import (
    cotations_de,
    creer_risque,
    dernieres_cotations,
    lister_risques,
    obtenir_risque,
    reevaluer,
    revues_dues as revues_dues_service,
    matrice_criticite,
    vers_sortie,
)

router = APIRouter(prefix="/risques", tags=["risques"])

# Taille bornée pour un import de référentiel, cohérent avec la limite déjà
# posée pour le parc d'équipements (prompt 3.1).
TAILLE_MAX_IMPORT_OCTETS = 5 * 1024 * 1024


@router.post("", response_model=RisqueSortie, status_code=status.HTTP_201_CREATED)
def creer(
    payload: RisqueCreation,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(require_role(*Permissions.GERER_RISQUES)),
) -> RisqueSortie:
    risque = creer_risque(db, payload, auteur_id=utilisateur.id)
    cotation = dernieres_cotations(db, [risque.id]).get(risque.id)
    return vers_sortie(risque, cotation)


@router.get("", response_model=list[RisqueSortie])
def lister(
    niveau: NiveauRisque | None = None,
    categorie: CategorieRisque | None = None,
    unite_travail: str | None = None,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_current_user),
) -> list[RisqueSortie]:
    # Consultation ouverte à tout le personnel (section 5.2.5, Acteurs :
    # "Consultation : ensemble du personnel").
    return [vers_sortie(r, c) for r, c in lister_risques(db, niveau=niveau, categorie=categorie, unite_travail=unite_travail)]


@router.get("/matrice", response_model=list[CelluleMatrice])
def matrice(
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_current_user),
) -> list[dict]:
    return matrice_criticite(db)


@router.get("/revues-dues", response_model=list[RevueDueSortie])
def lister_revues_dues(
    horizon_jours: int = 60,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_current_user),
) -> list[dict]:
    return revues_dues_service(db, horizon_jours)


@router.get("/{risque_id}", response_model=RisqueDetailSortie)
def lire(
    risque_id: int,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_current_user),
) -> RisqueDetailSortie:
    risque = obtenir_risque(db, risque_id)
    cotations = cotations_de(db, risque_id)
    sortie = vers_sortie(risque, cotations[0] if cotations else None)
    return RisqueDetailSortie(
        **sortie.model_dump(),
        cotations=[CotationSortie.model_validate(c) for c in cotations],
    )


@router.post("/{risque_id}/reevaluer", response_model=CotationSortie, status_code=status.HTTP_201_CREATED)
def reevaluer_route(
    risque_id: int,
    payload: CotationEntree,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(require_role(*Permissions.GERER_RISQUES)),
) -> CotationSortie:
    risque = obtenir_risque(db, risque_id)
    cotation = reevaluer(db, risque, payload, auteur_id=utilisateur.id)
    return CotationSortie.model_validate(cotation)


@router.post("/import", response_model=RapportImportRisques)
async def importer(
    fichier: UploadFile,
    date_evaluation: date | None = Form(None),
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(require_role(*Permissions.GERER_RISQUES)),
) -> RapportImportRisques:
    contenu = await fichier.read()
    if len(contenu) > TAILLE_MAX_IMPORT_OCTETS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Fichier trop volumineux : {len(contenu) / 1024 / 1024:.1f} Mo (5 Mo maximum)",
        )
    return importer_registre(db, contenu, fichier.filename or "", date_evaluation, auteur_id=utilisateur.id)

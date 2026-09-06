"""Routes du module Documents (prompt 4.3, section 5.3.5 du CDC)."""
from datetime import date

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_role
from app.core.fichiers import enregistrer_documents
from app.core.permissions import Permissions
from app.db.session import get_db
from app.models.document import Document
from app.models.enums import ConfidentialiteDocument
from app.models.utilisateur import Utilisateur
from app.schemas.document import AlerteRevueDocumentSortie, DocumentCreation, DocumentSortie
from app.services.document_service import (
    accuser_lecture,
    alertes_revue,
    approuver,
    creer_document,
    lister_documents,
    nouvelle_version,
    obtenir_document,
    soumettre_approbation,
    visible_par,
)

router = APIRouter(prefix="/documents", tags=["documents"])


def _recuperer_visible(db: Session, document_id: int, utilisateur: Utilisateur) -> Document:
    document = obtenir_document(db, document_id)
    if not visible_par(document, utilisateur):
        # 404, pas 403 : un document en brouillon/approbation n'existe pas du
        # point de vue d'un utilisateur qui n'y a pas droit (règle 5.3.5 :
        # "n'est pas accessible aux utilisateurs finaux").
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document introuvable")
    return document


@router.post("", response_model=DocumentSortie, status_code=status.HTTP_201_CREATED)
async def creer_document_route(
    reference: str = Form(...),
    intitule: str = Form(...),
    niveau: int = Form(...),
    confidentialite: ConfidentialiteDocument = Form(ConfidentialiteDocument.NORMAL),
    date_revue: date | None = Form(None),
    fichier: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(require_role(*Permissions.GERER_DOCUMENTS)),
) -> Document:
    donnees = DocumentCreation(
        reference=reference, intitule=intitule, niveau=niveau, confidentialite=confidentialite, date_revue=date_revue
    )
    chemin = (await enregistrer_documents([fichier], sous_dossier="documents"))[0] if fichier else None
    return creer_document(db, donnees, chemin, redacteur_id=utilisateur.id)


@router.get("", response_model=list[DocumentSortie])
def lister_documents_route(
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_current_user),
) -> list[Document]:
    return lister_documents(db, utilisateur)


@router.get("/alertes-revue", response_model=list[AlerteRevueDocumentSortie])
def alertes_revue_route(
    horizon_jours: int = 30,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(require_role(*Permissions.GERER_DOCUMENTS)),
) -> list[dict]:
    return alertes_revue(db, horizon_jours)


@router.get("/{document_id}", response_model=DocumentSortie)
def lire_document_route(
    document_id: int,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_current_user),
) -> Document:
    return _recuperer_visible(db, document_id, utilisateur)


@router.post("/{document_id}/soumettre-approbation", response_model=DocumentSortie)
def soumettre_approbation_route(
    document_id: int,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(require_role(*Permissions.GERER_DOCUMENTS)),
) -> Document:
    document = obtenir_document(db, document_id)
    return soumettre_approbation(db, document, modifie_par_id=utilisateur.id)


@router.post("/{document_id}/approuver", response_model=DocumentSortie)
def approuver_route(
    document_id: int,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(require_role(*Permissions.APPROUVER_DOCUMENTS)),
) -> Document:
    document = obtenir_document(db, document_id)
    return approuver(db, document, approbateur_id=utilisateur.id)


@router.post("/{document_id}/nouvelle-version", response_model=DocumentSortie, status_code=status.HTTP_201_CREATED)
async def nouvelle_version_route(
    document_id: int,
    fichier: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(require_role(*Permissions.GERER_DOCUMENTS)),
) -> Document:
    document = obtenir_document(db, document_id)
    chemin = (await enregistrer_documents([fichier], sous_dossier="documents"))[0] if fichier else None
    return nouvelle_version(db, document, chemin, redacteur_id=utilisateur.id)


@router.post("/{document_id}/accuser-lecture", response_model=DocumentSortie)
def accuser_lecture_route(
    document_id: int,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_current_user),
) -> Document:
    # Ouvert à tout utilisateur authentifié, pour SA PROPRE lecture — section
    # 5.3.5, "ensemble du personnel" en consultation, chacun accuse pour lui.
    document = _recuperer_visible(db, document_id, utilisateur)
    return accuser_lecture(db, document, utilisateur_id=utilisateur.id)

"""Routes du module Documents (prompt 4.3, section 5.3.5 du CDC)."""
from datetime import date
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.deps import get_current_user, require_role
from app.core.fichiers import enregistrer_documents
from app.core.permissions import Permissions
from app.db.session import get_db
from app.models.document import Document
from app.models.enums import ConfidentialiteDocument
from app.models.utilisateur import Utilisateur
from app.schemas.document import (
    AlerteRevueDocumentSortie,
    DocumentCreation,
    DocumentModification,
    DocumentSortie,
)
from app.services.document_service import (
    accuser_lecture,
    alertes_revue,
    approuver,
    creer_document,
    lister_documents,
    modifier_document,
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
    """Crée un document en statut brouillon. Il suit le cycle brouillon ->
    en_approbation -> en_vigueur et n'est visible des utilisateurs ordinaires
    qu'une fois en vigueur."""
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
    """Liste les documents visibles par l'utilisateur connecté — un document non
    encore en vigueur n'apparaît que pour son rédacteur et ses approbateurs."""
    return lister_documents(db, utilisateur)


@router.get("/alertes-revue", response_model=list[AlerteRevueDocumentSortie])
def alertes_revue_route(
    horizon_jours: int = 30,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(require_role(*Permissions.GERER_DOCUMENTS)),
) -> list[dict]:
    """Liste les documents dont la date de revue arrive à échéance dans
    l'horizon donné."""
    return alertes_revue(db, horizon_jours)


@router.get("/{document_id}", response_model=DocumentSortie)
def lire_document_route(
    document_id: int,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_current_user),
) -> Document:
    """Récupère un document par son identifiant. Renvoie 404 (pas 403) si le
    document n'est pas encore en vigueur et que l'appelant n'est ni rédacteur ni
    approbateur, pour ne pas révéler son existence."""
    return _recuperer_visible(db, document_id, utilisateur)


@router.patch("/{document_id}", response_model=DocumentSortie)
def modifier_document_route(
    document_id: int,
    payload: DocumentModification,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(require_role(*Permissions.GERER_DOCUMENTS)),
) -> Document:
    """Corrige les métadonnées d'un document en brouillon (référence, intitulé,
    niveau, confidentialité, date de revue)."""
    document = obtenir_document(db, document_id)
    return modifier_document(db, document, payload, modifie_par_id=utilisateur.id)


@router.get("/{document_id}/fichier")
def telecharger_fichier_route(
    document_id: int,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_current_user),
) -> FileResponse:
    """Télécharge le fichier joint au document (prompt 6.2 : sert de cible aux
    références cliquables de l'assistant documentaire). Mêmes règles de
    visibilité que la lecture du document — 404 si aucun fichier n'est joint."""
    document = _recuperer_visible(db, document_id, utilisateur)
    if not document.fichier:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aucun fichier joint à ce document")
    chemin = Path(settings.storage_dir) / document.fichier
    if not chemin.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fichier introuvable")
    return FileResponse(chemin, filename=f"{document.reference}-v{document.version}{chemin.suffix}")


@router.post("/{document_id}/soumettre-approbation", response_model=DocumentSortie)
def soumettre_approbation_route(
    document_id: int,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(require_role(*Permissions.GERER_DOCUMENTS)),
) -> Document:
    """Fait passer un document du statut brouillon au statut en_approbation."""
    document = obtenir_document(db, document_id)
    return soumettre_approbation(db, document, modifie_par_id=utilisateur.id)


@router.post("/{document_id}/approuver", response_model=DocumentSortie)
def approuver_route(
    document_id: int,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(require_role(*Permissions.APPROUVER_DOCUMENTS)),
) -> Document:
    """Approuve un document en attente : il passe en vigueur et devient visible
    de l'ensemble des utilisateurs autorisés. Réservé aux approbateurs."""
    document = obtenir_document(db, document_id)
    return approuver(db, document, approbateur_id=utilisateur.id)


@router.post("/{document_id}/nouvelle-version", response_model=DocumentSortie, status_code=status.HTTP_201_CREATED)
async def nouvelle_version_route(
    document_id: int,
    fichier: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(require_role(*Permissions.GERER_DOCUMENTS)),
) -> Document:
    """Crée une nouvelle version d'un document existant, qui repart en
    brouillon."""
    document = obtenir_document(db, document_id)
    chemin = (await enregistrer_documents([fichier], sous_dossier="documents"))[0] if fichier else None
    return nouvelle_version(db, document, chemin, redacteur_id=utilisateur.id)


@router.post("/{document_id}/accuser-lecture", response_model=DocumentSortie)
def accuser_lecture_route(
    document_id: int,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_current_user),
) -> Document:
    """Enregistre l'accusé de lecture de l'appelant sur un document en vigueur —
    chacun accuse lecture pour lui-même, ouvert à tout utilisateur authentifié."""
    # Ouvert à tout utilisateur authentifié, pour SA PROPRE lecture — section
    # 5.3.5, "ensemble du personnel" en consultation, chacun accuse pour lui.
    document = _recuperer_visible(db, document_id, utilisateur)
    return accuser_lecture(db, document, utilisateur_id=utilisateur.id)

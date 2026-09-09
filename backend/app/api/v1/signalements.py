"""Routes du module Signalements (prompt 1.1)."""
from datetime import datetime

from fastapi import APIRouter, Depends, File, Form, HTTPException, Response, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_role
from app.core.fichiers import enregistrer_photos
from app.core.permissions import Permissions
from app.db.session import get_db
from app.models.enums import RoleUtilisateur, StatutSignalement, TypeSignalement
from app.models.site import Site
from app.models.signalement import Signalement
from app.models.utilisateur import Utilisateur
from app.schemas.signalement import SignalementSortie, StatutMiseAJour
from app.services.signalement_service import archiver, changer_statut, creer_signalement, generer_pdf

router = APIRouter(prefix="/signalements", tags=["signalements"])

NOMBRE_MAX_PHOTOS = 5

# Chapitre 4 du CDC : le technicien n'a "lecture de ses propres saisies" ; le
# collaborateur, de même, n'est pas cité parmi les rôles de consultation large
# ("Consultation : responsables et direction", section 5.2.1 Acteurs). Ces deux
# rôles ne voient donc que leurs propres signalements non anonymes.
ROLES_VISIBILITE_RESTREINTE = {RoleUtilisateur.TECHNICIEN, RoleUtilisateur.COLLABORATEUR}


def _visible_par(signalement: Signalement, utilisateur: Utilisateur) -> bool:
    if utilisateur.role not in ROLES_VISIBILITE_RESTREINTE:
        return True
    return signalement.auteur_id == utilisateur.id


@router.post("", response_model=SignalementSortie, status_code=status.HTTP_201_CREATED)
async def creer(
    type: TypeSignalement = Form(...),
    site_id: int = Form(...),
    lieu: str = Form(...),
    description: str = Form(...),
    anonyme: bool = Form(False),
    date_constat: datetime = Form(...),
    photos: list[UploadFile] = File(default=[]),
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_current_user),
) -> Signalement:
    """Crée un signalement, avec photos optionnelles. Peut être anonyme
    (`anonyme=true`) : dans ce cas aucun utilisateur n'est jamais lié au
    signalement, y compris dans les journaux."""
    chemins_photos = await enregistrer_photos(photos, sous_dossier="signalements", nombre_max=NOMBRE_MAX_PHOTOS)

    return creer_signalement(
        db,
        type_=type,
        site_id=site_id,
        lieu=lieu,
        description=description,
        anonyme=anonyme,
        date_constat=date_constat,
        photos=chemins_photos,
        auteur=utilisateur,
    )


@router.get("", response_model=list[SignalementSortie])
def lister(
    statut: StatutSignalement | None = None,
    site_id: int | None = None,
    type: TypeSignalement | None = None,
    date_debut: datetime | None = None,
    date_fin: datetime | None = None,
    limite: int = 50,
    decalage: int = 0,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_current_user),
) -> list[Signalement]:
    """Liste les signalements avec filtres et pagination. Technicien et
    collaborateur ne voient que leurs propres signalements ; les autres rôles
    voient l'ensemble."""
    requete = select(Signalement).where(Signalement.archive.is_(False))

    if statut is not None:
        requete = requete.where(Signalement.statut == statut)
    if site_id is not None:
        requete = requete.where(Signalement.site_id == site_id)
    if type is not None:
        requete = requete.where(Signalement.type == type)
    if date_debut is not None:
        requete = requete.where(Signalement.date_constat >= date_debut)
    if date_fin is not None:
        requete = requete.where(Signalement.date_constat <= date_fin)

    if utilisateur.role in ROLES_VISIBILITE_RESTREINTE:
        requete = requete.where(Signalement.auteur_id == utilisateur.id)

    requete = requete.order_by(Signalement.date_saisie.desc()).offset(decalage).limit(min(limite, 200))

    return list(db.scalars(requete))


@router.get("/{signalement_id}", response_model=SignalementSortie)
def lire(
    signalement_id: int,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_current_user),
) -> Signalement:
    """Récupère un signalement par son identifiant. Renvoie 404 (pas 403) s'il
    est hors du périmètre de visibilité de l'appelant, pour ne pas confirmer
    son existence."""
    signalement = db.get(Signalement, signalement_id)
    if signalement is None or not _visible_par(signalement, utilisateur):
        # 404 plutôt que 403 : ne pas confirmer l'existence d'un signalement que
        # l'appelant n'a pas le droit de consulter (a fortiori s'il est anonyme).
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Signalement introuvable")
    return signalement


@router.get("/{signalement_id}/export-pdf")
def exporter_pdf(
    signalement_id: int,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_current_user),
) -> Response:
    """Génère le PDF d'un signalement, sous la même règle de visibilité (404 si
    hors périmètre) que la consultation."""
    signalement = db.get(Signalement, signalement_id)
    if signalement is None or not _visible_par(signalement, utilisateur):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Signalement introuvable")
    site = db.get(Site, signalement.site_id)
    auteur = db.get(Utilisateur, signalement.auteur_id) if signalement.auteur_id else None
    contenu = generer_pdf(signalement, site, auteur)
    return Response(
        content=contenu,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{signalement.reference}.pdf"'},
    )


@router.patch("/{signalement_id}/statut", response_model=SignalementSortie)
def mettre_a_jour_statut(
    signalement_id: int,
    payload: StatutMiseAJour,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(require_role(*Permissions.TRAITER_SIGNALEMENTS)),
) -> Signalement:
    """Change le statut de traitement d'un signalement. Réservé aux rôles
    habilités à traiter les signalements."""
    signalement = db.get(Signalement, signalement_id)
    if signalement is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Signalement introuvable")
    return changer_statut(db, signalement, payload.statut, modifie_par_id=utilisateur.id)


@router.post("/{signalement_id}/archiver", response_model=SignalementSortie)
def archiver_route(
    signalement_id: int,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(require_role(*Permissions.TRAITER_SIGNALEMENTS)),
) -> Signalement:
    """Archive un signalement (jamais de suppression physique)."""
    signalement = db.get(Signalement, signalement_id)
    if signalement is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Signalement introuvable")
    return archiver(db, signalement, modifie_par_id=utilisateur.id)

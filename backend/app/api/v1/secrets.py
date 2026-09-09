"""Routes du module Coffre-fort (CDC section 5.2.4)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_role
from app.core.permissions import Permissions
from app.db.session import get_db
from app.models.equipement import Equipement
from app.models.secret import Secret
from app.models.utilisateur import Utilisateur
from app.schemas.secret import (
    EntreeJournalAccesSortie,
    GenerationMotDePasseEntree,
    GenerationMotDePasseSortie,
    SecretConsultationSortie,
    SecretCreation,
    SecretModification,
    SecretSortie,
)
from app.services.secret_service import (
    archiver_secret,
    consulter_secret,
    creer_secret,
    generer_mot_de_passe,
    journal_du_secret,
    lister_secrets,
    modifier_secret,
    obtenir_secret_pour_journal,
    obtenir_secret_visible,
)

router = APIRouter(prefix="/secrets", tags=["coffre-fort"])


@router.post("", response_model=SecretSortie, status_code=status.HTTP_201_CREATED)
def creer_secret_route(
    payload: SecretCreation,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(require_role(*Permissions.GERER_SECRETS)),
) -> Secret:
    """Enregistre un secret rattaché à un équipement de l'inventaire (5.2.4).
    Réservé au responsable et à l'administrateur."""
    if payload.equipement_id is not None and db.get(Equipement, payload.equipement_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Équipement introuvable")
    return creer_secret(db, payload, cree_par_id=utilisateur.id)


@router.get("", response_model=list[SecretSortie])
def lister_secrets_route(
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_current_user),
) -> list[Secret]:
    """Liste les secrets visibles par l'appelant — un secret dont le rôle
    minimal requis dépasse le sien n'apparaît pas dans la liste."""
    return lister_secrets(db, utilisateur)


@router.get("/{secret_id}", response_model=SecretSortie)
def lire_secret_route(
    secret_id: int,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_current_user),
) -> Secret:
    """Fiche d'un secret (métadonnées seules, jamais la valeur — voir POST
    .../consulter)."""
    return obtenir_secret_visible(db, secret_id, utilisateur)


@router.patch("/{secret_id}", response_model=SecretSortie)
def modifier_secret_route(
    secret_id: int,
    payload: SecretModification,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(require_role(*Permissions.GERER_SECRETS)),
) -> Secret:
    """Modifie un secret en place (libellé, rattachement, valeur...) —
    réservé au responsable et à l'administrateur, indépendamment du
    `role_requis` du secret visé (ce sont les mêmes rôles qui gèrent le
    coffre-fort, quel que soit le niveau de confidentialité d'un secret
    donné)."""
    secret = db.get(Secret, secret_id)
    if secret is None or secret.archive:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Secret introuvable")
    if payload.equipement_id is not None and db.get(Equipement, payload.equipement_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Équipement introuvable")
    return modifier_secret(db, secret, payload, modifie_par_id=utilisateur.id)


@router.post("/{secret_id}/archiver", response_model=SecretSortie)
def archiver_secret_route(
    secret_id: int,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(require_role(*Permissions.GERER_SECRETS)),
) -> Secret:
    """Archive un secret (jamais de suppression physique, point 2 de
    CLAUDE.md)."""
    secret = db.get(Secret, secret_id)
    if secret is None or secret.archive:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Secret introuvable")
    return archiver_secret(db, secret, modifie_par_id=utilisateur.id)


@router.post("/{secret_id}/consulter", response_model=SecretConsultationSortie)
def consulter_secret_route(
    secret_id: int,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_current_user),
) -> dict:
    """Déchiffre et renvoie la valeur du secret — chaque appel enregistre une
    ligne dans le journal des accès (règle 5.2.4 : "toute consultation est
    enregistrée avec l'identité de l'utilisateur, l'horodatage et le secret
    concerné"). Le masquage automatique après quelques secondes est un
    comportement d'affichage, assuré côté client."""
    secret = obtenir_secret_visible(db, secret_id, utilisateur)
    valeur = consulter_secret(db, secret, utilisateur)
    return {"id": secret.id, "libelle": secret.libelle, "valeur": valeur}


@router.get("/{secret_id}/journal", response_model=list[EntreeJournalAccesSortie])
def journal_du_secret_route(
    secret_id: int,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(require_role(*Permissions.CONSULTER_JOURNAL_SECRETS)),
):
    """Journal des accès à un secret donné — écriture seule (aucune route ne
    permet de le modifier ou de le supprimer, règle 5.2.4 / point 4 de
    CLAUDE.md).

    Revue de sécurité du 2026-09-08 : passe par obtenir_secret_pour_journal(),
    pas un simple db.get() — sans ça, un responsable pouvait consulter le
    journal d'un secret dont `role_requis` est "administrateur" (qui du
    coup n'apparaît ni dans sa liste ni sur sa fiche, mais dont le journal
    restait accessible en devinant l'id) : la même règle de visibilité par
    secret que toutes les autres routes du module doit s'appliquer ici
    aussi, pas seulement le rôle global responsable/administrateur qui gère
    le coffre-fort dans l'ensemble. À la différence de obtenir_secret_visible(),
    n'exclut pas les secrets archivés : le journal doit rester consultable
    après archivage (voir docstring de obtenir_secret_pour_journal).
    """
    secret = obtenir_secret_pour_journal(db, secret_id, utilisateur)
    return journal_du_secret(db, secret.id)


@router.post("/generer-mot-de-passe", response_model=GenerationMotDePasseSortie)
def generer_mot_de_passe_route(
    payload: GenerationMotDePasseEntree,
    utilisateur: Utilisateur = Depends(require_role(*Permissions.GERER_SECRETS)),
) -> dict:
    """Génère un mot de passe fort respectant une politique paramétrable
    (longueur, symboles) — 5.2.4. Ne persiste rien : à l'appelant de
    l'utiliser ensuite dans un POST /secrets."""
    return {"mot_de_passe": generer_mot_de_passe(payload.longueur, payload.inclure_symboles)}

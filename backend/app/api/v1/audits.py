"""Routes du module Audits (prompt 4.2, section 5.3.4 du CDC)."""
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_role
from app.core.permissions import Permissions
from app.db.session import get_db
from app.models.campagne_audit import CampagneAudit
from app.models.exigence_audit import ExigenceAudit
from app.models.utilisateur import Utilisateur
from app.schemas.audit import (
    CampagneCreation,
    CampagneDetailSortie,
    CampagneSortie,
    ComparaisonCampagnes,
    CommentaireEntree,
    CotationEntree,
    CotationSortie,
    ExigenceAuditSortie,
)
from app.services.audit_service import (
    calculer_score,
    cloturer_campagne,
    comparer_campagnes,
    cotations_de_campagne,
    creer_campagne,
    generer_commentaire,
    generer_pdf,
    lister_exigences,
    modifier_commentaire,
    obtenir_campagne,
    soumettre_cotations,
    valider_commentaire,
)

router = APIRouter(prefix="/audits", tags=["audits"])


@router.get("/exigences", response_model=list[ExigenceAuditSortie])
def lister_exigences_route(
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_current_user),
) -> list[ExigenceAudit]:
    """Liste les exigences du référentiel d'audit."""
    return lister_exigences(db)


@router.post("/campagnes", response_model=CampagneSortie, status_code=status.HTTP_201_CREATED)
def creer_campagne_route(
    payload: CampagneCreation,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(require_role(*Permissions.GERER_AUDITS)),
) -> CampagneAudit:
    """Crée une campagne d'audit."""
    return creer_campagne(db, payload, auditeur_id=utilisateur.id)


@router.get("/campagnes/{campagne_id}", response_model=CampagneDetailSortie)
def lire_campagne_route(
    campagne_id: int,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_current_user),
) -> CampagneDetailSortie:
    """Récupère une campagne d'audit avec ses cotations et son score calculé
    (score total, taux de conformité, répartition par chapitre)."""
    campagne = obtenir_campagne(db, campagne_id)
    score = calculer_score(db, campagne_id)
    cotations = cotations_de_campagne(db, campagne_id)
    return CampagneDetailSortie(
        **CampagneSortie.model_validate(campagne).model_dump(),
        cotations=[CotationSortie.model_validate(c) for c in cotations],
        score_total=score["score_total"],
        score_maximal=score["score_maximal"],
        taux_conformite_pourcent=score["taux_conformite_pourcent"],
        interpretation=score["interpretation"],
        score_par_chapitre=score["score_par_chapitre"],
    )


@router.patch("/campagnes/{campagne_id}/cotations", response_model=list[CotationSortie])
def soumettre_cotations_route(
    campagne_id: int,
    payload: list[CotationEntree],
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(require_role(*Permissions.GERER_AUDITS)),
):
    """Soumet les cotations d'une campagne d'audit — 0 (absent), 1 (partiel) ou
    2 (conforme) par exigence."""
    campagne = obtenir_campagne(db, campagne_id)
    return soumettre_cotations(db, campagne, payload, modifie_par_id=utilisateur.id)


@router.post("/campagnes/{campagne_id}/cloturer", response_model=CampagneSortie)
def cloturer_campagne_route(
    campagne_id: int,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(require_role(*Permissions.GERER_AUDITS)),
) -> CampagneAudit:
    """Clôture une campagne d'audit."""
    campagne = obtenir_campagne(db, campagne_id)
    return cloturer_campagne(db, campagne, modifie_par_id=utilisateur.id)


@router.post("/campagnes/{campagne_id}/commentaire/generer", response_model=CampagneSortie)
def generer_commentaire_route(
    campagne_id: int,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(require_role(*Permissions.GERER_AUDITS)),
) -> CampagneAudit:
    """Pré-rédige (ou régénère) le commentaire de synthèse à partir du score
    réel de la campagne — brouillon, jamais exporté avant validation (prompt
    6.4)."""
    campagne = obtenir_campagne(db, campagne_id)
    return generer_commentaire(db, campagne, utilisateur.id)


@router.patch("/campagnes/{campagne_id}/commentaire", response_model=CampagneSortie)
def modifier_commentaire_route(
    campagne_id: int,
    payload: CommentaireEntree,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(require_role(*Permissions.GERER_AUDITS)),
) -> CampagneAudit:
    """Édite librement le commentaire (texte vide = repartir d'un document
    vierge) ; repasse en brouillon."""
    campagne = obtenir_campagne(db, campagne_id)
    return modifier_commentaire(db, campagne, payload.texte, modifie_par_id=utilisateur.id)


@router.post("/campagnes/{campagne_id}/commentaire/valider", response_model=CampagneSortie)
def valider_commentaire_route(
    campagne_id: int,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(require_role(*Permissions.GERER_AUDITS)),
) -> CampagneAudit:
    """Valide le commentaire : il devient une saisie humaine ordinaire, tracée
    à l'auteur de la validation, et apparaît désormais dans l'export PDF."""
    campagne = obtenir_campagne(db, campagne_id)
    return valider_commentaire(db, campagne, valide_par_id=utilisateur.id)


@router.get("/campagnes/{campagne_id}/export-pdf")
def exporter_pdf(
    campagne_id: int,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_current_user),
) -> Response:
    """Génère le PDF d'une campagne d'audit."""
    campagne = obtenir_campagne(db, campagne_id)
    auditeur = db.get(Utilisateur, campagne.auditeur_id)
    contenu = generer_pdf(db, campagne, auditeur)
    return Response(
        content=contenu,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{campagne.reference}.pdf"'},
    )


@router.get("/comparaison", response_model=ComparaisonCampagnes)
def comparer_route(
    reference_id: int,
    comparee_id: int,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_current_user),
) -> dict:
    """Compare les scores de deux campagnes d'audit."""
    return comparer_campagnes(db, reference_id, comparee_id)

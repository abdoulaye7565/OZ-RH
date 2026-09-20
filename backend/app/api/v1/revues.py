"""Routes du module Revues de direction (prompt 4.2, section 5.3.4 du CDC)."""
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.core.deps import require_role
from app.core.permissions import Permissions
from app.db.session import get_db
from app.models.decision_revue import DecisionRevue
from app.models.revue_direction import RevueDirection
from app.models.utilisateur import Utilisateur
from app.schemas.revue import (
    CommentaireEntree,
    DecisionCreation,
    DecisionSortie,
    RevueCreation,
    RevueDetailSortie,
    RevueSortie,
)
from app.services.revue_service import (
    creer_decision,
    creer_revue,
    decisions_de,
    generer_commentaire,
    generer_pdf,
    lister_revues,
    modifier_commentaire,
    obtenir_decision,
    obtenir_revue,
    solder_decision,
    valider_commentaire,
)

router = APIRouter(prefix="/revues", tags=["revues"])

# Module réservé à la direction (section 5.3.4, Acteurs : "Revue : direction") —
# voir Permissions.GERER_REVUES pour le rapprochement avec la matrice de rôles.
# Aucune route de consultation ouverte à tous n'est prévue ici, contrairement à
# Formations/Audits qui distinguent explicitement gestion et consultation.


@router.post("", response_model=RevueSortie, status_code=status.HTTP_201_CREATED)
def creer_revue_route(
    payload: RevueCreation,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(require_role(*Permissions.GERER_REVUES)),
) -> RevueDirection:
    """Crée une revue de direction. Module réservé à la direction, sans route de
    consultation ouverte à tout le personnel."""
    return creer_revue(db, payload, redacteur_id=utilisateur.id)


@router.get("", response_model=list[RevueSortie])
def lister_revues_route(
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(require_role(*Permissions.GERER_REVUES)),
) -> list[RevueDirection]:
    """Liste les revues de direction déjà créées (2026-09-19) — sans cette
    route, aucun moyen de retrouver une revue une fois l'écran de création
    quitté."""
    return lister_revues(db)


@router.get("/{revue_id}", response_model=RevueDetailSortie)
def lire_revue_route(
    revue_id: int,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(require_role(*Permissions.GERER_REVUES)),
) -> RevueDetailSortie:
    """Récupère une revue de direction avec ses décisions."""
    revue = obtenir_revue(db, revue_id)
    decisions = decisions_de(db, revue_id)
    sortie = RevueSortie.model_validate(revue)
    return RevueDetailSortie(
        **sortie.model_dump(), decisions=[DecisionSortie.model_validate(d) for d in decisions]
    )


@router.get("/{revue_id}/export-pdf")
def exporter_pdf(
    revue_id: int,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(require_role(*Permissions.GERER_REVUES)),
) -> Response:
    """Génère le PDF d'une revue de direction."""
    revue = obtenir_revue(db, revue_id)
    redacteur = db.get(Utilisateur, revue.redacteur_id)
    contenu = generer_pdf(db, revue, redacteur)
    return Response(
        content=contenu,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{revue.reference}.pdf"'},
    )


@router.post("/{revue_id}/commentaire/generer", response_model=RevueSortie)
def generer_commentaire_route(
    revue_id: int,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(require_role(*Permissions.GERER_REVUES)),
) -> RevueDirection:
    """Pré-rédige (ou régénère) le commentaire de synthèse à partir des
    indicateurs déjà figés de la revue — brouillon, jamais exporté avant
    validation (prompt 6.4)."""
    revue = obtenir_revue(db, revue_id)
    return generer_commentaire(db, revue, utilisateur.id)


@router.patch("/{revue_id}/commentaire", response_model=RevueSortie)
def modifier_commentaire_route(
    revue_id: int,
    payload: CommentaireEntree,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(require_role(*Permissions.GERER_REVUES)),
) -> RevueDirection:
    """Édite librement le commentaire (texte vide = repartir d'un document
    vierge) ; repasse en brouillon."""
    revue = obtenir_revue(db, revue_id)
    return modifier_commentaire(db, revue, payload.texte, modifie_par_id=utilisateur.id)


@router.post("/{revue_id}/commentaire/valider", response_model=RevueSortie)
def valider_commentaire_route(
    revue_id: int,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(require_role(*Permissions.GERER_REVUES)),
) -> RevueDirection:
    """Valide le commentaire : il devient une saisie humaine ordinaire, tracée
    à l'auteur de la validation, et apparaît désormais dans l'export PDF."""
    revue = obtenir_revue(db, revue_id)
    return valider_commentaire(db, revue, valide_par_id=utilisateur.id)


@router.post("/{revue_id}/decisions", response_model=DecisionSortie, status_code=status.HTTP_201_CREATED)
def creer_decision_route(
    revue_id: int,
    payload: DecisionCreation,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(require_role(*Permissions.GERER_REVUES)),
) -> DecisionRevue:
    """Ajoute une décision à une revue de direction."""
    revue = obtenir_revue(db, revue_id)
    return creer_decision(db, revue, payload, cree_par_id=utilisateur.id)


@router.post("/decisions/{decision_id}/solder", response_model=DecisionSortie)
def solder_decision_route(
    decision_id: int,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(require_role(*Permissions.GERER_REVUES)),
) -> DecisionRevue:
    """Marque une décision de revue de direction comme soldée."""
    decision = obtenir_decision(db, decision_id)
    return solder_decision(db, decision, modifie_par_id=utilisateur.id)

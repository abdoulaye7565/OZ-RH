"""Routes du service d'assistance (prompt 6.2, chapitre 16 du CDC)."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.utilisateur import Utilisateur
from app.schemas.assistance import QuestionDocumentaireEntree, ReferenceSortie, ReponseDocumentaireSortie
from app.services.assistance import repondre

router = APIRouter(prefix="/assistance", tags=["assistance"])


@router.post("/question-documentaire", response_model=ReponseDocumentaireSortie)
def question_documentaire_route(
    payload: QuestionDocumentaireEntree,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_current_user),
) -> ReponseDocumentaireSortie:
    """Répond à une question en langage naturel à partir des seuls documents en
    vigueur, avec leurs références. Ouvert à tout utilisateur authentifié
    (16.2.1 : "rendre la documentation... réellement accessible aux équipes de
    terrain", pas réservé à un rôle de gestion). Ne lève jamais d'erreur si le
    service est indisponible : voir `disponible` dans la réponse."""
    resultat = repondre(db, question=payload.question, utilisateur_id=utilisateur.id)
    return ReponseDocumentaireSortie(
        disponible=resultat.disponible,
        reponse_trouvee=resultat.reponse_trouvee,
        reponse=resultat.reponse,
        references=[
            ReferenceSortie(document_id=r.document_id, reference=r.reference, intitule=r.intitule, section=r.section)
            for r in resultat.references
        ],
    )

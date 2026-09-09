"""Schémas Pydantic du service d'assistance (prompt 6.2, chapitre 16 du CDC)."""
from pydantic import BaseModel


class QuestionDocumentaireEntree(BaseModel):
    question: str


class ReferenceSortie(BaseModel):
    document_id: int
    reference: str
    intitule: str
    section: str


class ReponseDocumentaireSortie(BaseModel):
    # `disponible=False` : service injoignable (mode dégradé) — distinct de
    # `reponse_trouvee=False`, qui signifie que le service a répondu mais que
    # la documentation ne couvre pas la question (16.2.1 : "l'assistant
    # l'indique explicitement").
    disponible: bool
    reponse_trouvee: bool
    reponse: str
    references: list[ReferenceSortie]

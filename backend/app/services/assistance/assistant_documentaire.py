"""Assistant documentaire (prompt 6.2, chapitre 16.2.1 et 16.3.2 du CDC) —
première fonction métier du lot 6 à exercer réellement le socle du prompt 6.1.

Recherche puis génération : la réponse n'est jamais générée « à l'aveugle ».
Si aucun segment du corpus ne dépasse le seuil de pertinence, la réponse est
directement le message de non-réponse — sans même appeler le modèle de
génération. C'est délibéré : le CDC qualifie cette garantie de "critère
d'acceptation, pas un détail" (16.2.1), une réponse fiable à 100 % dans ce cas
vaut mieux qu'une réponse probable selon la docilité du modèle."""
from dataclasses import dataclass, field

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.segment_document import SegmentDocument
from app.services.assistance import client, configuration, embeddings

NOMBRE_SEGMENTS_RETENUS = 5
SEUIL_SIMILARITE_MINIMUM = 0.3

MESSAGE_ABSENCE_DE_REPONSE = (
    "La documentation en vigueur ne permet pas de répondre à cette question."
)

_INSTRUCTION_SYSTEME = (
    "Tu es l'assistant documentaire du système SHEQ d'Hirondelles IT Lab. Réponds "
    "UNIQUEMENT à partir des extraits fournis ci-dessous, en citant à chaque "
    "affirmation le document et la section d'origine (ex. « (POL-SHEQ-001, "
    "Consignes de sécurité) »). Si les extraits ne permettent pas de répondre à la "
    "question, réponds exactement : « " + MESSAGE_ABSENCE_DE_REPONSE + " » — ne "
    "produis jamais de réponse plausible non appuyée sur les extraits fournis."
)


@dataclass
class ReferenceSegment:
    document_id: int
    reference: str
    intitule: str
    section: str


@dataclass
class ReponseAssistantDocumentaire:
    disponible: bool
    reponse_trouvee: bool
    reponse: str = ""
    references: list[ReferenceSegment] = field(default_factory=list)
    erreur: str | None = None


def _cosinus(a: list[float], b: list[float]) -> float:
    produit = sum(x * y for x, y in zip(a, b))
    norme_a = sum(x * x for x in a) ** 0.5
    norme_b = sum(x * x for x in b) ** 0.5
    if norme_a == 0 or norme_b == 0:
        return 0.0
    return produit / (norme_a * norme_b)


def repondre(db: Session, *, question: str, utilisateur_id: int) -> ReponseAssistantDocumentaire:
    if not configuration.fonction_activee("assistant_documentaire", db):
        return ReponseAssistantDocumentaire(
            disponible=False, reponse_trouvee=False, erreur="Assistant documentaire désactivé"
        )

    resultat_question = embeddings.calculer(
        db, fonction="assistant_documentaire", textes=[question], type_entree="query", utilisateur_id=utilisateur_id
    )
    if not resultat_question.disponible or not resultat_question.vecteurs:
        return ReponseAssistantDocumentaire(
            disponible=False, reponse_trouvee=False, erreur=resultat_question.erreur
        )
    vecteur_question = resultat_question.vecteurs[0]

    lignes = db.execute(
        select(SegmentDocument, Document).join(Document, SegmentDocument.document_id == Document.id)
    ).all()

    classement = sorted(
        ((_cosinus(vecteur_question, segment.embedding), segment, document) for segment, document in lignes),
        key=lambda t: t[0],
        reverse=True,
    )
    retenus = [(score, segment, document) for score, segment, document in classement if score >= SEUIL_SIMILARITE_MINIMUM][
        :NOMBRE_SEGMENTS_RETENUS
    ]

    if not retenus:
        return ReponseAssistantDocumentaire(disponible=True, reponse_trouvee=False, reponse=MESSAGE_ABSENCE_DE_REPONSE)

    extraits = "\n\n".join(
        f"[{document.reference} — {segment.section}]\n{segment.texte}" for _score, segment, document in retenus
    )
    prompt = f"{_INSTRUCTION_SYSTEME}\n\nExtraits disponibles :\n\n{extraits}\n\nQuestion : {question}"

    resultat_generation = client.appeler(
        db, fonction="assistant_documentaire", prompt=prompt, utilisateur_id=utilisateur_id
    )
    if not resultat_generation.disponible or resultat_generation.contenu is None:
        return ReponseAssistantDocumentaire(
            disponible=False, reponse_trouvee=False, erreur=resultat_generation.erreur
        )

    reponse_trouvee = MESSAGE_ABSENCE_DE_REPONSE not in resultat_generation.contenu
    references = [
        ReferenceSegment(document_id=document.id, reference=document.reference, intitule=document.intitule, section=segment.section)
        for _score, segment, document in retenus
    ] if reponse_trouvee else []

    return ReponseAssistantDocumentaire(
        disponible=True, reponse_trouvee=reponse_trouvee,
        reponse=resultat_generation.contenu, references=references,
    )

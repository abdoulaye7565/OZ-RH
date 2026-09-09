"""Indexation des documents en vigueur (prompt 6.2, chapitre 16.3.2 du CDC).

Appelée depuis `document_service.approuver()` : indexe la version qui devient
`EN_VIGUEUR`, retire les segments de celle qui devient `ARCHIVE` — les deux
événements du même appel, exactement comme le décrit le CDC ("indexés lors de
leur approbation" / "les segments issus d'une version archivée sont
retirés")."""
from pathlib import Path

from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.document import Document
from app.models.segment_document import SegmentDocument
from app.services.assistance import decoupage, embeddings, extraction


def indexer_document(db: Session, document: Document) -> bool:
    """Ne lève jamais d'exception : un document non indexable (pas de fichier,
    format non reconnu, service d'embeddings indisponible) reste simplement
    absent du corpus — l'approbation elle-même ne doit jamais échouer pour
    cette raison ("le mode dégradé est la norme"). Renvoie `True` si
    l'indexation a effectivement produit des segments."""
    if not document.fichier:
        return False

    chemin = Path(settings.storage_dir) / document.fichier
    sections = extraction.extraire_sections(str(chemin))
    if not sections:
        return False

    morceaux: list[tuple[str, str]] = [
        (section, segment) for section, texte in sections for segment in decoupage.decouper(texte)
    ]
    if not morceaux:
        return False

    resultat = embeddings.calculer(
        db, fonction="indexation_documentaire", textes=[m[1] for m in morceaux], type_entree="document"
    )
    if not resultat.disponible:
        return False

    retirer_segments(db, document.id)
    for position, ((section, texte), vecteur) in enumerate(zip(morceaux, resultat.vecteurs)):
        db.add(SegmentDocument(document_id=document.id, section=section, texte=texte, embedding=vecteur, position=position))
    db.commit()
    return True


def retirer_segments(db: Session, document_id: int) -> None:
    db.execute(delete(SegmentDocument).where(SegmentDocument.document_id == document_id))
    db.commit()

"""Logique métier du module Documents (prompt 4.3, section 5.3.5 du CDC,
PRO-SHEQ-004 « Procédure de maîtrise documentaire »)."""
from datetime import date, datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.enums import ConfidentialiteDocument, RoleUtilisateur, StatutDocument
from app.models.utilisateur import Utilisateur
from app.schemas.document import DocumentCreation

# Section 5.3.5 : "Un document en cours d'approbation n'est pas accessible aux
# utilisateurs finaux." Les rôles ci-dessous voient tous les statuts (rédaction,
# approbation, gestion) ; les autres ne voient que la version en vigueur et les
# archives (PRO-SHEQ-004, § 5 : "chaque collaborateur : n'utiliser que la
# version en vigueur").
ROLES_VOIENT_TOUS_STATUTS = {RoleUtilisateur.REFERENT_SHEQ, RoleUtilisateur.RESPONSABLE, RoleUtilisateur.ADMINISTRATEUR}

# Alerte de revue (5.3.5 : "être alerté des documents arrivant à échéance de
# revue") — le CDC ne donne pas d'horizon pour les documents précisément, mais
# la table des notifications (chapitre 6.3) cite "trente jours avant" pour les
# échéances en général.
HORIZON_ALERTE_REVUE_JOURS = 30


def _prochaine_version(version_actuelle: str) -> str:
    """PRO-SHEQ-004, § 3 : "toute modification crée une nouvelle version
    (01 → 02)" — incrémentation numérique à deux chiffres, comme l'exemple
    donné littéralement."""
    return f"{int(version_actuelle) + 1:02d}"


def creer_document(db: Session, donnees: DocumentCreation, fichier: str | None, redacteur_id: int) -> Document:
    document = Document(
        reference=donnees.reference,
        intitule=donnees.intitule,
        niveau=donnees.niveau,
        version="01",
        redacteur_id=redacteur_id,
        statut=StatutDocument.BROUILLON,
        date_revue=donnees.date_revue,
        confidentialite=donnees.confidentialite,
        fichier=fichier,
        cree_par_id=redacteur_id,
    )
    db.add(document)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Cette référence/version existe déjà"
        )
    db.refresh(document)
    return document


def obtenir_document(db: Session, document_id: int) -> Document:
    document = db.get(Document, document_id)
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document introuvable")
    return document


def visible_par(document: Document, utilisateur: Utilisateur) -> bool:
    if utilisateur.role in ROLES_VOIENT_TOUS_STATUTS or document.redacteur_id == utilisateur.id:
        return True
    return document.statut in (StatutDocument.EN_VIGUEUR, StatutDocument.ARCHIVE)


def lister_documents(db: Session, utilisateur: Utilisateur) -> list[Document]:
    documents = db.scalars(select(Document).order_by(Document.reference, Document.version))
    return [d for d in documents if visible_par(d, utilisateur)]


def soumettre_approbation(db: Session, document: Document, modifie_par_id: int) -> Document:
    if document.statut != StatutDocument.BROUILLON:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Seul un document en brouillon peut être soumis à approbation"
        )
    document.statut = StatutDocument.EN_APPROBATION
    document.modifie_par_id = modifie_par_id
    db.commit()
    db.refresh(document)
    return document


def approuver(db: Session, document: Document, approbateur_id: int) -> Document:
    """Règle 5.3.5 : "Approuver un document, la version antérieure passant
    automatiquement en archive." Recherche la version EN_VIGUEUR précédente
    de la même référence (il ne peut y en avoir qu'une, règle 5.3.5 : "une
    seule version... en vigueur à un instant donné") et l'archive."""
    if document.statut != StatutDocument.EN_APPROBATION:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Seul un document en cours d'approbation peut être approuvé"
        )

    version_precedente = db.scalar(
        select(Document).where(
            Document.reference == document.reference,
            Document.statut == StatutDocument.EN_VIGUEUR,
            Document.id != document.id,
        )
    )
    if version_precedente is not None:
        version_precedente.statut = StatutDocument.ARCHIVE
        version_precedente.modifie_par_id = approbateur_id

    document.statut = StatutDocument.EN_VIGUEUR
    document.approbateur_id = approbateur_id
    document.modifie_par_id = approbateur_id
    db.commit()
    db.refresh(document)
    return document


def nouvelle_version(db: Session, document_actuel: Document, fichier: str | None, redacteur_id: int) -> Document:
    if document_actuel.statut != StatutDocument.EN_VIGUEUR:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Une nouvelle version ne peut être créée qu'à partir de la version en vigueur",
        )
    nouveau = Document(
        reference=document_actuel.reference,
        intitule=document_actuel.intitule,
        niveau=document_actuel.niveau,
        version=_prochaine_version(document_actuel.version),
        redacteur_id=redacteur_id,
        statut=StatutDocument.BROUILLON,
        date_revue=document_actuel.date_revue,
        confidentialite=document_actuel.confidentialite,
        fichier=fichier if fichier is not None else document_actuel.fichier,
        cree_par_id=redacteur_id,
    )
    db.add(nouveau)
    db.commit()
    db.refresh(nouveau)
    return nouveau


def accuser_lecture(db: Session, document: Document, utilisateur_id: int) -> Document:
    if document.statut != StatutDocument.EN_VIGUEUR:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Seule la version en vigueur peut être accusée de lecture"
        )
    accuses = list(document.accuses_lecture or [])
    if any(a["utilisateur_id"] == utilisateur_id for a in accuses):
        return document  # déjà accusé — idempotent, pas d'erreur ni de doublon
    accuses.append({"utilisateur_id": utilisateur_id, "date": datetime.now(timezone.utc).isoformat()})
    document.accuses_lecture = accuses
    db.commit()
    db.refresh(document)
    return document


def alertes_revue(db: Session, horizon_jours: int = HORIZON_ALERTE_REVUE_JOURS) -> list[dict]:
    aujourdhui = date.today()
    documents = db.scalars(
        select(Document).where(
            Document.statut == StatutDocument.EN_VIGUEUR,
            Document.date_revue.is_not(None),
            Document.archive.is_(False),
        )
    )
    resultats = []
    for d in documents:
        jours_restants = (d.date_revue - aujourdhui).days
        if jours_restants <= horizon_jours:
            resultats.append(
                {
                    "document_id": d.id,
                    "reference": d.reference,
                    "intitule": d.intitule,
                    "date_revue": d.date_revue,
                    "jours_restants": jours_restants,
                    "due": True,
                }
            )
    return sorted(resultats, key=lambda r: r["jours_restants"])

"""Génération paresseuse de références ENR-SHEQ-AAAA-NNN (point 7, CLAUDE.md ;
chapitre 14 du CDC, cas de test 12) pour les entités qui n'en avaient jamais
eu besoin avant l'export PDF (prompt 5.1) : EvaluationSlam, Inspection,
CampagneAudit, RevueDirection. Signalement, Permis et Configuration ont déjà
leur propre référence assignée à la création (SIG-AAAA-NNN, AAAA-NNN,
ENR-SHEQ-AAAA-NNN respectivement) — inchangés, ce module ne les concerne pas.

Une séquence par TABLE, pas une séquence globale partagée entre types
d'enregistrement : même principe déjà en vigueur pour CONFIGURATION depuis le
prompt 3.2 (sa colonne `reference` est unique à sa propre table, sans lien
avec celle d'une autre entité)."""
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session


def obtenir_ou_generer_reference(db: Session, objet, modele) -> str:
    if objet.reference:
        return objet.reference

    annee = datetime.now(timezone.utc).year
    prefixe = f"ENR-SHEQ-{annee}-"
    dernier = db.scalar(
        select(modele.reference)
        .where(modele.reference.like(f"{prefixe}%"))
        .order_by(modele.reference.desc())
        .limit(1)
    )
    prochain_numero = int(dernier.rsplit("-", 1)[-1]) + 1 if dernier else 1
    objet.reference = f"{prefixe}{prochain_numero:03d}"
    db.commit()
    db.refresh(objet)
    return objet.reference

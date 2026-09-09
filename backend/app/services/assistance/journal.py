"""Journalisation des appels au service d'assistance (prompt 6.1, tableau 10 :
"chaque appel est journalisé avec sa fonction, son volume et son coût estimé,
et restitué dans un tableau de suivi")."""
from datetime import date, datetime, timezone

from sqlalchemy import extract, func, select
from sqlalchemy.orm import Session

from app.models.appel_assistance import AppelAssistance


def enregistrer_appel(
    db: Session,
    *,
    fonction: str,
    utilisateur_id: int | None,
    volume_caracteres: int,
    duree_ms: int,
    cout_estime_usd: float | None,
    succes: bool,
) -> AppelAssistance:
    """Un échec est journalisé au même titre qu'un succès — voir le docstring
    du modèle. Jamais appelée dans un `except` qui avalerait par ailleurs
    l'erreur : c'est `client.appeler` qui journalise, succès ou échec, avant
    de retourner son résultat à l'appelant."""
    entree = AppelAssistance(
        fonction=fonction,
        utilisateur_id=utilisateur_id,
        volume_caracteres=volume_caracteres,
        duree_ms=duree_ms,
        cout_estime_usd=cout_estime_usd,
        succes=succes,
    )
    db.add(entree)
    db.commit()
    db.refresh(entree)
    return entree


def depense_du_mois(db: Session, *, mois_reference: date | None = None) -> float:
    """Somme des coûts estimés des appels réussis du mois en cours (ou du mois
    donné). Les appels en échec n'ont généralement aucun coût réel (voir
    `cout_estime_usd` nullable) et ne participent donc pas au total même s'ils
    en portaient un par erreur — seul un appel réussi consomme le plafond."""
    reference = mois_reference or datetime.now(timezone.utc).date()
    total = db.scalar(
        select(func.coalesce(func.sum(AppelAssistance.cout_estime_usd), 0.0)).where(
            AppelAssistance.succes.is_(True),
            extract("year", AppelAssistance.horodatage) == reference.year,
            extract("month", AppelAssistance.horodatage) == reference.month,
        )
    )
    return float(total or 0.0)

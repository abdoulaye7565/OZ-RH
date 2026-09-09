"""Activation par fonction et plafond mensuel (prompt 6.1, tableau 10 : "Le
mode dégradé est la norme" et "Le coût est maîtrisé et suivi"; chapitre 16.4 :
"un plafond mensuel est paramétrable ; son atteinte désactive les fonctions
non essentielles et alerte l'administrateur")."""
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.config import settings
from app.services import notification_service
from app.services.assistance import journal


def fonction_activee(cle: str, db: Session | None = None, *, essentielle: bool = False) -> bool:
    """Une fonction n'est active que si l'interrupteur général ET son propre
    indicateur le sont — jamais l'un sans l'autre (tableau 10 : "un indicateur
    de configuration permet d'activer ou de désactiver CHAQUE fonction
    indépendamment", en plus de l'interrupteur général du socle) — ET, pour
    une fonction non essentielle, si le plafond mensuel n'est pas dépassé.

    Aucune fonction métier n'existe encore à ce prompt (6.1) : le champ
    `Settings.assistance_{cle}_active` correspondant n'existe donc pour
    aucune valeur de `cle` pour l'instant, et cette fonction renvoie toujours
    False en pratique tant qu'un prompt ultérieur (6.2...) n'ajoute pas son
    propre indicateur — comportement attendu, pas un défaut : une fonction
    inconnue du système de configuration est une fonction indisponible.

    `db` optionnel : une fonction marquée `essentielle=True` n'a jamais besoin
    de vérifier le plafond, donc jamais besoin de session — aucune fonction
    n'est essentielle par défaut (mode dégradé par défaut, pas l'inverse)."""
    if not settings.assistance_activee:
        return False
    if not bool(getattr(settings, f"assistance_{cle}_active", False)):
        return False
    if not essentielle and db is not None and plafond_depasse(db):
        return False
    return True


def plafond_depasse(db: Session) -> bool:
    """Sans plafond configuré, jamais dépassé — un déploiement peut activer le
    socle sans avoir encore arbitré de budget avec la direction (16.6). Alerte
    l'administrateur à chaque appel tant que le dépassement persiste : la
    déduplication par mois (voir `notifier_plafond_assistance_atteint`) évite
    la répétition, une seule notification par mois et par administrateur."""
    if settings.assistance_plafond_mensuel_usd is None:
        return False

    depense = journal.depense_du_mois(db)
    depasse = depense >= settings.assistance_plafond_mensuel_usd
    if depasse:
        aujourdhui = datetime.now(timezone.utc)
        notification_service.notifier_plafond_assistance_atteint(
            db, annee=aujourdhui.year, mois_numero=aujourdhui.month,
            depense_usd=depense, plafond_usd=settings.assistance_plafond_mensuel_usd,
        )
    return depasse

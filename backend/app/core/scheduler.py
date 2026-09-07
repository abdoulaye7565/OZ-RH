"""Planificateur de tâches (prompt 4.4). APScheduler plutôt que Celery : la
volumétrie du projet (une poignée de vérifications quotidiennes) ne justifie
pas une file de tâches distribuée avec worker séparé — un `BackgroundScheduler`
synchrone, dans le même processus que l'API, suffit très largement.

Démarré/arrêté via le cycle de vie de l'application FastAPI (voir app/main.py).
`settings.scheduler_actif` permet de le désactiver — utilisé par
tests/conftest.py pour qu'aucun job planifié ne s'exécute pendant les tests
(le job ouvrirait sa propre session sur la base réelle, jamais celle,
en mémoire, substituée pour les tests)."""
import logging

from apscheduler.schedulers.background import BackgroundScheduler

from app.core.config import settings
from app.db.session import SessionLocal
from app.services.notification_service import executer_taches_planifiees

logger = logging.getLogger("app.notifications")

_planificateur: BackgroundScheduler | None = None

# Heure d'exécution quotidienne — le CDC ne précise pas d'heure ; choisie tôt
# le matin (avant l'arrivée des équipes) pour que les rappels du jour soient
# déjà visibles à la prise de poste.
HEURE_EXECUTION_QUOTIDIENNE = 6


def _executer_taches_planifiees_job() -> None:
    db = SessionLocal()
    try:
        rapport = executer_taches_planifiees(db)
        logger.info("Tâches planifiées exécutées : %s", rapport)
    finally:
        db.close()


def demarrer_planificateur() -> None:
    global _planificateur
    if not settings.scheduler_actif or _planificateur is not None:
        return
    _planificateur = BackgroundScheduler()
    _planificateur.add_job(
        _executer_taches_planifiees_job,
        trigger="cron",
        hour=HEURE_EXECUTION_QUOTIDIENNE,
        minute=0,
        id="rappels_echeance_quotidiens",
    )
    _planificateur.start()
    logger.info("Planificateur démarré (exécution quotidienne à %dh00)", HEURE_EXECUTION_QUOTIDIENNE)


def arreter_planificateur() -> None:
    global _planificateur
    if _planificateur is not None:
        _planificateur.shutdown(wait=False)
        _planificateur = None

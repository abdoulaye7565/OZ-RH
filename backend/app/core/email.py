"""Envoi de courriels (prompt 4.4, chapitre 6.3 du CDC). `smtplib` de la
bibliothèque standard : le CDC ne demande aucun service tiers particulier, et
une simple connexion SMTP suffit au volume de ce projet — pas de nouvelle
dépendance pour ce seul besoin."""
import logging
import smtplib
from email.message import EmailMessage

from app.core.config import settings

logger = logging.getLogger("app.notifications")


def envoyer_courriel(destinataire: str, sujet: str, corps: str) -> tuple[bool, str | None]:
    """Renvoie (succès, message_erreur). Ne lève jamais d'exception : une
    panne d'envoi ne doit pas faire échouer l'action métier qui a déclenché la
    notification (ex. la création d'un signalement) — mais l'échec est
    renvoyé pour être enregistré sur la notification elle-même
    (Notification.courriel_erreur), jamais avalé en silence (CLAUDE.md, point 9)."""
    if not settings.smtp_hote:
        message = "SMTP non configuré (SMTP_HOTE vide) : envoi non tenté"
        logger.warning("Courriel à %s non envoyé : %s", destinataire, message)
        return False, message

    message_email = EmailMessage()
    message_email["Subject"] = sujet
    message_email["From"] = settings.smtp_expediteur
    message_email["To"] = destinataire
    message_email.set_content(corps)

    try:
        with smtplib.SMTP(settings.smtp_hote, settings.smtp_port, timeout=10) as serveur:
            serveur.starttls()
            if settings.smtp_utilisateur and settings.smtp_mot_de_passe:
                serveur.login(settings.smtp_utilisateur, settings.smtp_mot_de_passe)
            serveur.send_message(message_email)
        return True, None
    except (smtplib.SMTPException, OSError) as exc:
        logger.error("Échec d'envoi du courriel à %s : %s", destinataire, exc)
        return False, str(exc)

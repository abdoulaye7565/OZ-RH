"""Chiffrement symétrique des secrets du coffre-fort (CDC section 5.2.4).

Fernet (bibliothèque `cryptography`) plutôt qu'un chiffrement fait maison :
authentifié (AES-128-CBC + HMAC-SHA256), horodaté, et la bibliothèque de
référence recommandée pour ce cas d'usage en Python. La clé maîtresse
(`FERNET_MASTER_KEY`) vit hors base de données, dans la configuration
d'environnement (jamais dans Git, voir .env.example) — règle 5.2.4 du CDC :
"la clé maîtresse est conservée hors de la base de données".

Ce module échoue explicitement (`ValueError`) si la clé est absente ou mal
formée, au chargement — pas de mode dégradé silencieux qui laisserait un
secret partir en clair. `Settings.fernet_master_key` est déjà un champ
obligatoire (`app/core/config.py`, sans valeur par défaut) : l'absence de
clé fait déjà échouer le démarrage de l'API avant même d'atteindre ce
module ; l'erreur explicite ici couvre le cas d'une clé présente mais
invalide (mauvaise longueur, pas du base64 urlsafe attendu par Fernet).
"""
from cryptography.fernet import Fernet, InvalidToken

from app.core.config import settings

try:
    _fernet = Fernet(settings.fernet_master_key.encode("utf-8"))
except (ValueError, TypeError) as exc:
    raise ValueError(
        "FERNET_MASTER_KEY invalide : attendu une clé Fernet valide "
        "(python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\")"
    ) from exc


def chiffrer(valeur_claire: str) -> bytes:
    """Chiffre une chaîne en clair. Ne jamais journaliser `valeur_claire`
    (règle 5.2.4 : "aucun secret n'apparaît en clair... dans les journaux
    techniques")."""
    return _fernet.encrypt(valeur_claire.encode("utf-8"))


def dechiffrer(valeur_chiffree: bytes) -> str:
    """Déchiffre une valeur produite par `chiffrer`. Lève `InvalidToken` si
    la valeur est corrompue ou a été chiffrée avec une autre clé — jamais
    rattrapée silencieusement ici, à l'appelant de décider (point 9,
    CLAUDE.md : "ne pas masquer les erreurs")."""
    return _fernet.decrypt(valeur_chiffree).decode("utf-8")


__all__ = ["chiffrer", "dechiffrer", "InvalidToken"]

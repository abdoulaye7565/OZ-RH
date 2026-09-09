"""Garde-fous du service d'assistance (prompt 6.1, tableau 10 : "Les données
sensibles sont exclues" — "aucun identifiant du coffre-fort, aucun mot de
passe et aucune donnée nominative de santé n'est transmis")."""
import re

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.utilisateur import Utilisateur


class ContenuRefuseError(Exception):
    """Levée quand le contenu à transmettre au service d'assistance est refusé
    par un garde-fou — jamais capturée en silence par l'appelant : une
    fonction métier qui déclenche cette erreur a un défaut à corriger, pas un
    cas à absorber (CLAUDE.md, "ne masque pas les erreurs")."""


def verifier_pas_de_secret(contenu: object) -> None:
    """Refuse tout contenu de type `bytes` : dans cette base, seule une valeur
    chiffrée du coffre-fort (`Secret.valeur_chiffree`) est jamais du binaire —
    toute saisie utilisateur légitime est une chaîne de caractères. Un garde-fou
    structurel plutôt qu'une liste noire de noms de champs : il fonctionne même
    si l'appelant se trompe de champ ou renomme quelque chose."""
    if isinstance(contenu, bytes):
        raise ContenuRefuseError(
            "Contenu de type bytes refusé : jamais transmis au service d'assistance "
            "(seules les valeurs chiffrées du coffre-fort sont de ce type dans cette application)"
        )


_MOTIF_NOM = re.compile(r"[A-ZÀÂÄÉÈÊËÎÏÔÖÙÛÜÇ][\wÀ-ÿ'-]+")


def masquer_noms(texte: str, db: Session) -> str:
    """Remplace toute occurrence du nom ou du prénom d'un utilisateur connu par
    « [personne] ». Limite assumée et documentée (docs/JOURNAL.md, prompt 6.1) :
    ne masque que les personnes déjà enregistrées dans l'application — ni un
    visiteur, ni un tiers cité dans un texte libre, ni une variante orthographique.
    Un masquage déterministe par liste connue plutôt qu'un modèle de reconnaissance
    d'entités nommées, pour ne pas ajouter de dépendance lourde à ce socle."""
    noms = db.execute(select(Utilisateur.nom, Utilisateur.prenom)).all()
    a_masquer = {partie for ligne in noms for partie in ligne if partie}
    if not a_masquer:
        return texte

    def _remplacer(correspondance: re.Match) -> str:
        mot = correspondance.group(0)
        return "[personne]" if mot in a_masquer else mot

    return _MOTIF_NOM.sub(_remplacer, texte)

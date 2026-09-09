"""Client d'appel au service d'assistance externe (prompt 6.1, chapitre 16.3.1
du CDC : "Un module dédié expose les fonctions d'assistance ; aucun autre
composant n'appelle directement le service externe" et "Les appels sont
effectués côté serveur" — la clé ne quitte jamais ce module.

Fournisseur retenu : Anthropic (décision explicite prise avec l'utilisateur au
prompt 6.1, le CDC n'imposant aucun fournisseur). Appel REST direct via httpx
(déjà une dépendance du projet) plutôt que le SDK `anthropic` officiel : un seul
type de requête HTTP JSON est nécessaire à ce socle, une dépendance supplémentaire
ne se justifie pas pour ça — à reconsidérer si un prompt ultérieur a besoin de
fonctionnalités que le SDK apporterait (streaming, upload de fichiers...)."""
import time
from dataclasses import dataclass

import httpx
from sqlalchemy.orm import Session

from app.core.config import settings
from app.services.assistance import garde_fous, journal

_URL_ANTHROPIC = "https://api.anthropic.com/v1/messages"
_VERSION_API_ANTHROPIC = "2023-06-01"

# Tarifs approximatifs (USD par million de jetons), à vérifier/ajuster une fois
# un usage réel et une facturation observée disponibles (16.4 : "coût estimé" —
# le CDC ne demande pas une facturation exacte). Un seul modèle pour l'instant :
# à étendre en dictionnaire si `assistance_modele` devient configurable par appel.
_COUT_ENTREE_PAR_MILLION_USD = 1.0
_COUT_SORTIE_PAR_MILLION_USD = 5.0

_NOMBRE_MAX_TENTATIVES = 2  # 1 essai + 1 réessai, jamais plus (tableau 10 : "réessai limité")


@dataclass
class ResultatAppel:
    disponible: bool
    contenu: str | None = None
    erreur: str | None = None


def appeler(
    db: Session,
    *,
    fonction: str,
    prompt: str,
    utilisateur_id: int | None,
    max_jetons_sortie: int = 1024,
) -> ResultatAppel:
    """Point d'entrée unique vers le service externe. Ne lève jamais d'exception
    vers l'appelant (tableau 10 : "le mode dégradé est la norme") : toute
    indisponibilité — délai dépassé, erreur réseau, erreur du fournisseur —
    se traduit par `ResultatAppel(disponible=False, ...)`, jamais par une
    exception qui interromprait la fonctionnalité appelante. Journalise
    systématiquement toute tentative réelle d'appel — succès ou échec — dès
    lors que le garde-fou sur le contenu est passé ; un contenu refusé par
    `verifier_pas_de_secret` n'est PAS journalisé ici (ce n'est pas une
    tentative d'appel mais une erreur de code appelant, à corriger, pas une
    métrique d'usage du service)."""
    garde_fous.verifier_pas_de_secret(prompt)

    if settings.assistance_api_cle is None:
        journal.enregistrer_appel(
            db, fonction=fonction, utilisateur_id=utilisateur_id,
            volume_caracteres=len(prompt), duree_ms=0,
            cout_estime_usd=None, succes=False,
        )
        return ResultatAppel(disponible=False, erreur="assistance_api_cle non configurée")

    debut = time.monotonic()
    derniere_erreur = ""
    for tentative in range(1, _NOMBRE_MAX_TENTATIVES + 1):
        try:
            reponse = httpx.post(
                _URL_ANTHROPIC,
                headers={
                    "x-api-key": settings.assistance_api_cle,
                    "anthropic-version": _VERSION_API_ANTHROPIC,
                    "content-type": "application/json",
                },
                json={
                    "model": settings.assistance_modele,
                    "max_tokens": max_jetons_sortie,
                    "messages": [{"role": "user", "content": prompt}],
                },
                timeout=settings.assistance_delai_max_secondes,
            )
            reponse.raise_for_status()
            donnees = reponse.json()
            texte = "".join(bloc.get("text", "") for bloc in donnees.get("content", []))
            usage = donnees.get("usage", {})
            cout = _estimer_cout_usd(usage.get("input_tokens", 0), usage.get("output_tokens", 0))
            duree_ms = int((time.monotonic() - debut) * 1000)
            journal.enregistrer_appel(
                db, fonction=fonction, utilisateur_id=utilisateur_id,
                volume_caracteres=len(prompt), duree_ms=duree_ms,
                cout_estime_usd=cout, succes=True,
            )
            return ResultatAppel(disponible=True, contenu=texte)
        except (httpx.TimeoutException, httpx.NetworkError) as exc:
            derniere_erreur = f"{type(exc).__name__}: {exc}"
            continue  # transitoire : la boucle retente (jusqu'à _NOMBRE_MAX_TENTATIVES)
        except httpx.HTTPStatusError as exc:
            derniere_erreur = f"HTTP {exc.response.status_code}"
            break  # une erreur 4xx/5xx du fournisseur ne se corrige pas en réessayant

    duree_ms = int((time.monotonic() - debut) * 1000)
    journal.enregistrer_appel(
        db, fonction=fonction, utilisateur_id=utilisateur_id,
        volume_caracteres=len(prompt), duree_ms=duree_ms,
        cout_estime_usd=None, succes=False,
    )
    return ResultatAppel(disponible=False, erreur=derniere_erreur)


def _estimer_cout_usd(jetons_entree: int, jetons_sortie: int) -> float:
    return (
        jetons_entree / 1_000_000 * _COUT_ENTREE_PAR_MILLION_USD
        + jetons_sortie / 1_000_000 * _COUT_SORTIE_PAR_MILLION_USD
    )

"""Client d'appel au service de représentations vectorielles (prompt 6.2,
chapitre 16.3.1 : "aucun autre composant n'appelle directement le service
externe" — même principe d'isolation que `client.py` pour la génération de
texte). Fournisseur : Voyage AI (décision explicite, prompt 6.2 — Anthropic
n'expose aucune API d'embeddings publique)."""
import time
from dataclasses import dataclass

import httpx
from sqlalchemy.orm import Session

from app.core.config import settings
from app.services.assistance import garde_fous, journal

_URL_VOYAGE = "https://api.voyageai.com/v1/embeddings"

# Tarif approximatif (USD par million de jetons), même réserve que dans
# client.py : à ajuster une fois un usage réel facturé disponible.
_COUT_PAR_MILLION_USD = 0.02

_NOMBRE_MAX_TENTATIVES = 2


@dataclass
class ResultatEmbeddings:
    disponible: bool
    vecteurs: list[list[float]] | None = None
    erreur: str | None = None


def calculer(
    db: Session, *, fonction: str, textes: list[str], type_entree: str, utilisateur_id: int | None = None
) -> ResultatEmbeddings:
    """`type_entree` : "document" à l'indexation, "query" à la recherche — Voyage
    recommande de distinguer les deux pour la qualité de la similarité calculée
    ensuite. Même contrat que `client.appeler` : jamais d'exception vers
    l'appelant, toujours journalisé."""
    for texte in textes:
        garde_fous.verifier_pas_de_secret(texte)

    if settings.assistance_voyage_api_cle is None:
        journal.enregistrer_appel(
            db, fonction=fonction, utilisateur_id=utilisateur_id,
            volume_caracteres=sum(len(t) for t in textes), duree_ms=0,
            cout_estime_usd=None, succes=False,
        )
        return ResultatEmbeddings(disponible=False, erreur="assistance_voyage_api_cle non configurée")

    debut = time.monotonic()
    derniere_erreur = ""
    for _tentative in range(1, _NOMBRE_MAX_TENTATIVES + 1):
        try:
            reponse = httpx.post(
                _URL_VOYAGE,
                headers={"Authorization": f"Bearer {settings.assistance_voyage_api_cle}"},
                json={"input": textes, "model": settings.assistance_modele_embeddings, "input_type": type_entree},
                timeout=settings.assistance_delai_max_secondes,
            )
            reponse.raise_for_status()
            donnees = reponse.json()
            vecteurs = [ligne["embedding"] for ligne in sorted(donnees["data"], key=lambda l: l["index"])]
            jetons = donnees.get("usage", {}).get("total_tokens", 0)
            duree_ms = int((time.monotonic() - debut) * 1000)
            journal.enregistrer_appel(
                db, fonction=fonction, utilisateur_id=utilisateur_id,
                volume_caracteres=sum(len(t) for t in textes), duree_ms=duree_ms,
                cout_estime_usd=jetons / 1_000_000 * _COUT_PAR_MILLION_USD, succes=True,
            )
            return ResultatEmbeddings(disponible=True, vecteurs=vecteurs)
        except (httpx.TimeoutException, httpx.NetworkError) as exc:
            derniere_erreur = f"{type(exc).__name__}: {exc}"
            continue
        except httpx.HTTPStatusError as exc:
            derniere_erreur = f"HTTP {exc.response.status_code}"
            break

    duree_ms = int((time.monotonic() - debut) * 1000)
    journal.enregistrer_appel(
        db, fonction=fonction, utilisateur_id=utilisateur_id,
        volume_caracteres=sum(len(t) for t in textes), duree_ms=duree_ms,
        cout_estime_usd=None, succes=False,
    )
    return ResultatEmbeddings(disponible=False, erreur=derniere_erreur)

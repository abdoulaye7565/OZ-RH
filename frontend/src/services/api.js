const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";
const CLE_JETON = "sheq_access_token";
const CLE_JETON_RAFRAICHISSEMENT = "sheq_refresh_token";

function lire(cle) {
  try {
    return localStorage.getItem(cle);
  } catch {
    return null;
  }
}

function ecrire(cle, valeur) {
  try {
    if (valeur) localStorage.setItem(cle, valeur);
    else localStorage.removeItem(cle);
  } catch {
    // Stockage indisponible (navigation privée, quotas) : la session ne survit
    // simplement pas au rechargement, ce n'est pas bloquant pour l'usage courant.
  }
}

function lireJeton() {
  return lire(CLE_JETON);
}

function ecrireJeton(jeton) {
  ecrire(CLE_JETON, jeton);
}

function lireJetonRafraichissement() {
  return lire(CLE_JETON_RAFRAICHISSEMENT);
}

function ecrireJetonRafraichissement(jeton) {
  ecrire(CLE_JETON_RAFRAICHISSEMENT, jeton);
}

// Appelé quand le jeton d'accès ET le rafraîchissement ont tous deux échoué :
// injecté depuis main.js (plutôt qu'importé ici) pour qu'un service générique
// n'ait pas à connaître le store d'authentification ni le routeur.
let gestionnaireSessionExpiree = null;
function definirGestionnaireSessionExpiree(fn) {
  gestionnaireSessionExpiree = fn;
}

// Dédoublonne les rafraîchissements concurrents : si plusieurs requêtes
// essuient un 401 en même temps, une seule vraie tentative de rafraîchissement
// part, les autres attendent son résultat au lieu d'en déclencher chacune une.
let promesseRafraichissement = null;

async function rafraichirJeton() {
  if (!promesseRafraichissement) {
    promesseRafraichissement = (async () => {
      const refresh = lireJetonRafraichissement();
      if (!refresh) throw new Error("Aucun jeton de rafraîchissement disponible");
      const reponse = await fetch(`${API_URL}/api/v1/auth/rafraichissement`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh_token: refresh }),
      });
      if (!reponse.ok) throw new Error("Jeton de rafraîchissement invalide ou expiré");
      const donnees = await reponse.json();
      ecrireJeton(donnees.access_token);
      return donnees.access_token;
    })().finally(() => {
      promesseRafraichissement = null;
    });
  }
  return promesseRafraichissement;
}

// FastAPI renvoie `detail` sous 3 formes possibles : une chaîne (erreurs
// métier), une liste d'erreurs de validation Pydantic ([{loc, msg, type}]),
// ou (rarement) un objet unique de cette forme. Error.message doit rester
// une chaîne dans tous les cas, sinon l'interpolation template affiche
// "[object Object]" au lieu du message.
function extraireMessage(detail, statut) {
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail.map((e) => e?.msg ?? JSON.stringify(e)).join(" · ") || `Erreur ${statut}`;
  }
  if (detail && typeof detail === "object") return detail.msg ?? JSON.stringify(detail);
  return `Erreur ${statut}`;
}

class ErreurApi extends Error {
  constructor(message, statut, details) {
    super(message);
    this.statut = statut;
    this.details = details;
  }
}

/**
 * Requête JSON authentifiée. Ne fait AUCUNE validation métier : le serveur reste
 * la seule source de vérité, cette fonction ne fait que relayer sa réponse
 * (succès ou erreur) — voir CLAUDE.md, "ne pas remplacer la validation serveur".
 *
 * Jeton d'accès de courte durée (15 min, config.py) : un 401 sur une requête
 * qui portait un jeton tente un rafraîchissement silencieux (une seule fois,
 * `_relance` évite toute boucle) avant de rejouer la requête. Si le
 * rafraîchissement échoue aussi (refresh token expiré ou absent), la session
 * est considérée close : jetons effacés, gestionnaireSessionExpiree() prévenu
 * (redirection vers /connexion, câblée depuis main.js), et l'erreur 401
 * d'origine remonte normalement à l'appelant.
 */
async function requete(chemin, { methode = "GET", corps, entetes = {}, brut = false, _relance = false } = {}) {
  const jeton = lireJeton();
  const options = {
    method: methode,
    headers: { ...entetes, ...(jeton ? { Authorization: `Bearer ${jeton}` } : {}) },
  };

  if (corps instanceof FormData) {
    options.body = corps;
  } else if (corps !== undefined) {
    options.headers["Content-Type"] = "application/json";
    options.body = JSON.stringify(corps);
  }

  const reponse = await fetch(`${API_URL}${chemin}`, options);

  if (!reponse.ok) {
    if (reponse.status === 401 && jeton && !_relance && lireJetonRafraichissement()) {
      try {
        await rafraichirJeton();
        return requete(chemin, { methode, corps, entetes, brut, _relance: true });
      } catch {
        ecrireJeton(null);
        ecrireJetonRafraichissement(null);
        gestionnaireSessionExpiree?.();
        // Le rafraîchissement a échoué : on continue ci-dessous pour renvoyer
        // à l'appelant l'erreur 401 d'origine, pas une erreur générique.
      }
    }
    let details = null;
    try {
      details = await reponse.json();
    } catch {
      // corps de réponse non JSON (erreur réseau, 500 sans détail) : ignoré.
    }
    throw new ErreurApi(extraireMessage(details?.detail, reponse.status), reponse.status, details);
  }

  if (brut) return reponse;
  if (reponse.status === 204) return null;
  return reponse.json();
}

async function getHealth() {
  const reponse = await fetch(`${API_URL}/health`);
  if (!reponse.ok) throw new ErreurApi(`L'API a répondu avec le statut ${reponse.status}`, reponse.status);
  return reponse.json();
}

export default {
  API_URL,
  getHealth,
  requete,
  lireJeton,
  ecrireJeton,
  lireJetonRafraichissement,
  ecrireJetonRafraichissement,
  definirGestionnaireSessionExpiree,
  ErreurApi,
};

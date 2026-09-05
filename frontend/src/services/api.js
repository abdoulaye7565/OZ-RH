const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";
const CLE_JETON = "sheq_access_token";

function lireJeton() {
  try {
    return localStorage.getItem(CLE_JETON);
  } catch {
    return null;
  }
}

function ecrireJeton(jeton) {
  try {
    if (jeton) localStorage.setItem(CLE_JETON, jeton);
    else localStorage.removeItem(CLE_JETON);
  } catch {
    // Stockage indisponible (navigation privée, quotas) : la session ne survit
    // simplement pas au rechargement, ce n'est pas bloquant pour l'usage courant.
  }
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
 */
async function requete(chemin, { methode = "GET", corps, entetes = {}, brut = false } = {}) {
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
    let details = null;
    try {
      details = await reponse.json();
    } catch {
      // corps de réponse non JSON (erreur réseau, 500 sans détail) : ignoré.
    }
    throw new ErreurApi(details?.detail ?? `Erreur ${reponse.status}`, reponse.status, details);
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

export default { API_URL, getHealth, requete, lireJeton, ecrireJeton, ErreurApi };

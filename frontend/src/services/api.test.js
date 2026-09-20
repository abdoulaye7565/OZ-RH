import { beforeEach, describe, expect, it, vi } from "vitest";
import api from "./api";

// Couvre la logique introduite le 2026-09-08 (rafraîchissement automatique du
// jeton — voir docs/JOURNAL.md, "Points critiques", point 1) : premier test
// automatisé du projet pour ce fichier, jusqu'ici vérifié uniquement en
// navigateur réel (browser-automation). Le comportement offline (fetch qui
// rejette avec un TypeError) est couvert côté stores/signalements.js, pas ici
// — ce fichier ne fait que relayer l'erreur, il ne décide jamais de mettre en
// file.

function reponseJson(corps, statut = 200) {
  return {
    ok: statut >= 200 && statut < 300,
    status: statut,
    json: async () => corps,
  };
}

beforeEach(() => {
  localStorage.clear();
  vi.restoreAllMocks();
  api.definirGestionnaireSessionExpiree(null);
});

describe("extraction du message d'erreur (extraireMessage, via requete())", () => {
  it("une erreur métier (detail = chaîne) reste une chaîne", async () => {
    global.fetch = vi.fn().mockResolvedValue(reponseJson({ detail: "Identifiant ou mot de passe incorrect" }, 401));
    await expect(api.requete("/api/v1/x")).rejects.toMatchObject({
      message: "Identifiant ou mot de passe incorrect",
      statut: 401,
    });
  });

  it("une erreur de validation Pydantic (detail = liste) est jointe en une chaîne lisible", async () => {
    global.fetch = vi.fn().mockResolvedValue(
      reponseJson({ detail: [{ msg: "champ requis" }, { msg: "trop long" }] }, 422)
    );
    await expect(api.requete("/api/v1/x")).rejects.toMatchObject({
      message: "champ requis · trop long",
    });
  });

  it("un corps de réponse non JSON ne fait pas planter l'appelant", async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 500,
      json: async () => {
        throw new Error("pas du JSON");
      },
    });
    await expect(api.requete("/api/v1/x")).rejects.toMatchObject({ message: "Erreur 500" });
  });
});

describe("rafraîchissement automatique du jeton sur 401", () => {
  it("rafraîchit silencieusement puis rejoue la requête d'origine avec le nouveau jeton", async () => {
    api.ecrireJeton("access-perime");
    api.ecrireJetonRafraichissement("refresh-valide");

    const appels = [];
    global.fetch = vi.fn(async (url, options) => {
      appels.push({ url, autorisation: options?.headers?.Authorization });
      if (url.endsWith("/api/v1/auth/rafraichissement")) {
        return reponseJson({ access_token: "access-tout-neuf" });
      }
      if (url.endsWith("/api/v1/signalements")) {
        // Premier appel : jeton périmé → 401. Deuxième (après rafraîchissement) → 200.
        if (options.headers.Authorization === "Bearer access-perime") {
          return reponseJson({ detail: "Identifiants invalides ou expirés" }, 401);
        }
        return reponseJson([{ id: 1 }]);
      }
      throw new Error(`URL inattendue dans ce test : ${url}`);
    });

    const resultat = await api.requete("/api/v1/signalements");

    expect(resultat).toEqual([{ id: 1 }]);
    expect(api.lireJeton()).toBe("access-tout-neuf");
    // 3 appels réseau : requête d'origine (401) → rafraîchissement → requête rejouée.
    expect(appels).toHaveLength(3);
    expect(appels[2].autorisation).toBe("Bearer access-tout-neuf");
  });

  it("dédoublonne deux 401 concurrents : un seul appel réel à /auth/rafraichissement", async () => {
    api.ecrireJeton("access-perime");
    api.ecrireJetonRafraichissement("refresh-valide");

    let appelsRafraichissement = 0;
    global.fetch = vi.fn(async (url, options) => {
      if (url.endsWith("/api/v1/auth/rafraichissement")) {
        appelsRafraichissement += 1;
        return reponseJson({ access_token: "access-tout-neuf" });
      }
      if (options.headers.Authorization === "Bearer access-perime") {
        return reponseJson({}, 401);
      }
      return reponseJson({ ok: true });
    });

    await Promise.all([api.requete("/api/v1/a"), api.requete("/api/v1/b")]);

    expect(appelsRafraichissement).toBe(1);
  });

  it("si le rafraîchissement échoue aussi : jetons effacés, session signalée expirée, l'erreur 401 d'origine remonte", async () => {
    api.ecrireJeton("access-perime");
    api.ecrireJetonRafraichissement("refresh-perime");
    const gestionnaire = vi.fn();
    api.definirGestionnaireSessionExpiree(gestionnaire);

    global.fetch = vi.fn(async (url) => {
      if (url.endsWith("/api/v1/auth/rafraichissement")) {
        return reponseJson({ detail: "Jeton de rafraîchissement invalide ou expiré" }, 401);
      }
      return reponseJson({ detail: "Identifiants invalides ou expirés" }, 401);
    });

    await expect(api.requete("/api/v1/signalements")).rejects.toMatchObject({
      statut: 401,
      message: "Identifiants invalides ou expirés",
    });
    expect(api.lireJeton()).toBeNull();
    expect(api.lireJetonRafraichissement()).toBeNull();
    expect(gestionnaire).toHaveBeenCalledTimes(1);
  });

  it("ne tente aucun rafraîchissement quand la requête ne portait pas de jeton (ex. page de connexion)", async () => {
    global.fetch = vi.fn().mockResolvedValue(reponseJson({ detail: "Identifiant ou mot de passe incorrect" }, 401));

    await expect(api.requete("/api/v1/auth/connexion", { methode: "POST", corps: {} })).rejects.toMatchObject({
      statut: 401,
    });
    expect(global.fetch).toHaveBeenCalledTimes(1);
  });

  it("ne rafraîchit pas non plus s'il n'existe aucun refresh token stocké", async () => {
    api.ecrireJeton("access-perime");
    // Pas de refresh token écrit.
    global.fetch = vi.fn().mockResolvedValue(reponseJson({}, 401));

    await expect(api.requete("/api/v1/signalements")).rejects.toMatchObject({ statut: 401 });
    expect(global.fetch).toHaveBeenCalledTimes(1);
  });
});

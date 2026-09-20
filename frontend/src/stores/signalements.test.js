import "fake-indexeddb/auto";
import { createPinia, setActivePinia } from "pinia";
import { beforeEach, describe, expect, it, vi } from "vitest";

// Couvre la distinction introduite le 2026-09-08 (voir docs/JOURNAL.md,
// "Mode hors connexion" puis "Points critiques" point 1) : une erreur réseau
// (TypeError, on est hors ligne) doit mettre le signalement en file plutôt
// que de le perdre ; un vrai refus serveur (ErreurApi — 422, 401 après
// l'échec du rafraîchissement...) ne doit surtout PAS être mis en file, une
// nouvelle tentative donnerait le même résultat. La confusion entre les deux
// est exactement le bug réel qu'un 401 de session expirée avait provoqué
// avant le correctif du rafraîchissement automatique.

vi.mock("../services/api", () => {
  class ErreurApi extends Error {
    constructor(message, statut, details) {
      super(message);
      this.statut = statut;
      this.details = details;
    }
  }
  return {
    default: {
      requete: vi.fn(),
      ErreurApi,
      lireJeton: vi.fn(() => null),
      ecrireJeton: vi.fn(),
      lireJetonRafraichissement: vi.fn(() => null),
      ecrireJetonRafraichissement: vi.fn(),
      definirGestionnaireSessionExpiree: vi.fn(),
    },
  };
});

const { default: api } = await import("../services/api");
const { useSignalementsStore } = await import("./signalements");

const CHAMPS = {
  type: "accident",
  site_id: 1,
  lieu: "Pylône P-1",
  description: "Test",
  anonyme: false,
  date_constat: "2026-09-09T10:00:00Z",
};

beforeEach(() => {
  setActivePinia(createPinia());
  vi.clearAllMocks();
});

describe("creer() — offline vs vrai refus serveur", () => {
  it("une erreur réseau (TypeError) met le signalement en file, ne le perd pas", async () => {
    api.requete.mockRejectedValue(new TypeError("Failed to fetch"));
    const store = useSignalementsStore();

    const resultat = await store.creer(CHAMPS, []);

    expect(resultat.enAttente).toBe(true);
    expect(resultat.reference).toBeNull();
    expect(store.liste).toHaveLength(1);
    // toEqual (égalité profonde), pas toBe : Pinia enveloppe l'état dans un
    // Proxy réactif, store.liste[0] n'est donc pas le même objet référence
    // que la valeur renvoyée par l'action, seulement un contenu identique.
    expect(store.liste[0]).toEqual(resultat);
    expect(store.erreur).toBeNull(); // pas une erreur pour l'utilisateur : c'est le comportement attendu
  });

  it("un vrai refus serveur (ErreurApi) n'est jamais mis en file, remonte normalement", async () => {
    api.requete.mockRejectedValue(new api.ErreurApi("Le lieu est obligatoire", 422));
    const store = useSignalementsStore();

    await expect(store.creer(CHAMPS, [])).rejects.toMatchObject({ statut: 422 });

    expect(store.erreur).toBe("Le lieu est obligatoire");
    expect(store.liste).toHaveLength(0); // pas de placeholder fantôme pour une erreur définitive
  });

  it("un envoi réussi n'est pas mis en file, apparaît normalement", async () => {
    const signalementServeur = { id: 1, reference: "SIG-2026-001", statut: "nouveau", ...CHAMPS };
    api.requete.mockResolvedValue(signalementServeur);
    const store = useSignalementsStore();

    const resultat = await store.creer(CHAMPS, []);

    expect(resultat).toEqual(signalementServeur);
    expect(resultat.enAttente).toBeUndefined();
  });
});

describe("nombreParStatut — exclut les éléments en attente de réseau", () => {
  it("un signalement en attente ne compte dans aucun onglet de statut", () => {
    const store = useSignalementsStore();
    store.liste = [
      { id: 1, statut: "nouveau", enAttente: false },
      { id: "local-1", statut: "nouveau", enAttente: true },
    ];

    expect(store.nombreParStatut.nouveau).toBe(1);
  });
});

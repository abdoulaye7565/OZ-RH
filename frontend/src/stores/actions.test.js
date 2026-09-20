import { createPinia, setActivePinia } from "pinia";
import { beforeEach, describe, expect, it, vi } from "vitest";

// Couvre mettreAJourAvancement() / changerStatut() (2026-09-10, voir
// docs/JOURNAL.md) — ajouté suite à un retour direct de l'utilisateur ("on ne
// peut pas modifier le statut de l'action") : le back-end et le store
// exposaient déjà ces routes, mais aucune vue desktop ne les câblait et le
// store n'était pas testé. Le point sensible ici : un indicateur vide ne doit
// PAS être envoyé (sinon le serveur l'enregistre en "" et refuse ensuite la
// clôture).

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
const { useActionsStore } = await import("./actions");

beforeEach(() => {
  setActivePinia(createPinia());
  vi.clearAllMocks();
});

describe("mettreAJourAvancement()", () => {
  it("omet l'indicateur quand il est vide ou ne contient que des espaces", async () => {
    const store = useActionsStore();
    store.liste = [{ id: 7, avancement: 0, statut: "ouverte" }];
    api.requete.mockResolvedValue({ id: 7, avancement: 50, statut: "ouverte" });

    await store.mettreAJourAvancement(7, 50, "   ");

    expect(api.requete).toHaveBeenCalledWith("/api/v1/actions/7/avancement", {
      methode: "PATCH",
      corps: { avancement: 50 }, // pas de clé `indicateur`
    });
  });

  it("envoie l'indicateur nettoyé (trim) quand il est renseigné", async () => {
    const store = useActionsStore();
    store.liste = [{ id: 7, avancement: 0, statut: "ouverte" }];
    api.requete.mockResolvedValue({ id: 7, avancement: 80, statut: "ouverte", indicateur: "Fait" });

    await store.mettreAJourAvancement(7, 80, "  Fait  ");

    expect(api.requete).toHaveBeenCalledWith("/api/v1/actions/7/avancement", {
      methode: "PATCH",
      corps: { avancement: 80, indicateur: "Fait" },
    });
  });

  it("remplace la ligne correspondante dans la liste par la version serveur", async () => {
    const store = useActionsStore();
    store.liste = [{ id: 7, avancement: 0, statut: "ouverte" }];
    api.requete.mockResolvedValue({ id: 7, avancement: 60, statut: "ouverte", indicateur: null });

    await store.mettreAJourAvancement(7, 60, "");

    expect(store.liste[0].avancement).toBe(60);
  });
});

describe("changerStatut()", () => {
  it("appelle la route statut et met à jour la ligne", async () => {
    const store = useActionsStore();
    store.liste = [{ id: 3, statut: "ouverte" }];
    api.requete.mockResolvedValue({ id: 3, statut: "en_cours" });

    await store.changerStatut(3, "en_cours");

    expect(api.requete).toHaveBeenCalledWith("/api/v1/actions/3/statut", {
      methode: "PATCH",
      corps: { statut: "en_cours" },
    });
    expect(store.liste[0].statut).toBe("en_cours");
  });

  it("laisse remonter un refus serveur (transition invalide, 409)", async () => {
    const store = useActionsStore();
    store.liste = [{ id: 3, statut: "cloturee" }];
    api.requete.mockRejectedValue(new api.ErreurApi("Transition invalide", 409));

    await expect(store.changerStatut(3, "en_cours")).rejects.toMatchObject({ statut: 409 });
  });
});

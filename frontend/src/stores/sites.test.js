import { createPinia, setActivePinia } from "pinia";
import { beforeEach, describe, expect, it, vi } from "vitest";

// Couvre le store Sites (2026-09-10, retour direct de l'utilisateur : « on a
// un seul site alors que nous intervenons sur plusieurs sites »).

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
const { useSitesStore } = await import("./sites");

beforeEach(() => {
  setActivePinia(createPinia());
  vi.clearAllMocks();
});

describe("creer()", () => {
  it("poste le site puis recharge la liste", async () => {
    const store = useSitesStore();
    api.requete
      .mockResolvedValueOnce({ id: 9, nom: "Antenne Kayes", type: "client", adresse: null })
      .mockResolvedValueOnce([{ id: 9, nom: "Antenne Kayes", type: "client", adresse: null }]);

    await store.creer({ nom: "Antenne Kayes", type: "client", adresse: null });

    expect(api.requete).toHaveBeenNthCalledWith(1, "/api/v1/sites", {
      methode: "POST",
      corps: { nom: "Antenne Kayes", type: "client", adresse: null },
    });
    expect(store.liste).toHaveLength(1);
  });
});

describe("modifier()", () => {
  it("patch la bonne route et remplace la ligne en place", async () => {
    const store = useSitesStore();
    store.liste = [{ id: 3, nom: "Ancien", type: "client", adresse: null }];
    api.requete.mockResolvedValue({ id: 3, nom: "Ancien", type: "client", adresse: "Kayes centre" });

    await store.modifier(3, { adresse: "Kayes centre" });

    expect(api.requete).toHaveBeenCalledWith("/api/v1/sites/3", {
      methode: "PATCH",
      corps: { adresse: "Kayes centre" },
    });
    expect(store.liste[0].adresse).toBe("Kayes centre");
  });
});

describe("archiver()", () => {
  it("appelle la route archiver puis recharge", async () => {
    const store = useSitesStore();
    api.requete.mockResolvedValueOnce({ id: 5, archive: true }).mockResolvedValueOnce([]);

    await store.archiver(5);

    expect(api.requete).toHaveBeenNthCalledWith(1, "/api/v1/sites/5/archiver", { methode: "POST" });
  });

  it("laisse remonter un refus serveur (409, équipements rattachés)", async () => {
    const store = useSitesStore();
    api.requete.mockRejectedValue(new api.ErreurApi("2 équipement(s) y sont encore rattachés", 409));

    await expect(store.archiver(5)).rejects.toMatchObject({ statut: 409 });
  });
});

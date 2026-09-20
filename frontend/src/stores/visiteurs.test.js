import { createPinia, setActivePinia } from "pinia";
import { beforeEach, describe, expect, it, vi } from "vitest";

// Couvre archiver() (2026-09-09, retour direct de l'utilisateur — "on doit
// permettre d'archiver les visiteurs").

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
const { useVisiteursStore } = await import("./visiteurs");

beforeEach(() => {
  setActivePinia(createPinia());
  vi.clearAllMocks();
});

describe("archiver()", () => {
  it("appelle la bonne route puis recharge le registre", async () => {
    const store = useVisiteursStore();
    api.requete
      .mockResolvedValueOnce({ id: 1, archive: true }) // POST .../archiver
      .mockResolvedValueOnce([]) // GET .../presents (recharger)
      .mockResolvedValueOnce([]); // GET /visiteurs (recharger)

    await store.archiver(1);

    expect(api.requete).toHaveBeenNthCalledWith(1, "/api/v1/visiteurs/1/archiver", { methode: "POST" });
    expect(api.requete).toHaveBeenCalledTimes(3); // archiver + les 2 appels de charger()
  });

  it("un refus serveur (visiteur encore présent) remonte à l'appelant", async () => {
    const store = useVisiteursStore();
    api.requete.mockRejectedValue(new api.ErreurApi("Impossible d'archiver un visiteur encore présent sur site", 400));

    await expect(store.archiver(1)).rejects.toMatchObject({ statut: 400 });
  });
});

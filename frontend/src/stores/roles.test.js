import { createPinia, setActivePinia } from "pinia";
import { beforeEach, describe, expect, it, vi } from "vitest";

// Couvre useRolesStore (2026-09-10, retour direct de l'utilisateur — "les
// modules du sidebar ne s'affichent pas" : la barre latérale montrait des
// liens vers des écrans réservés à certains rôles côté serveur, sans le
// savoir. Ce store est la source unique qui doit empêcher ça de se
// reproduire.

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
const { useRolesStore } = await import("./roles");

const DONNEES = {
  roles: [
    { valeur: "administrateur", libelle: "Administrateur", perimetre: "Tout" },
    { valeur: "technicien", libelle: "Technicien", perimetre: "Terrain" },
  ],
  permissions: [
    { cle: "CONSULTER_TABLEAU_BORD", libelle: "Consulter le tableau de bord", roles: ["administrateur", "responsable"] },
    { cle: "GERER_UTILISATEURS", libelle: "Gérer les comptes utilisateurs", roles: ["administrateur"] },
  ],
};

beforeEach(() => {
  setActivePinia(createPinia());
  vi.clearAllMocks();
});

describe("charger()", () => {
  it("charge une seule fois par session (pas de re-fetch au second appel)", async () => {
    api.requete.mockResolvedValueOnce(DONNEES);
    const store = useRolesStore();
    await store.charger();
    await store.charger();
    expect(api.requete).toHaveBeenCalledTimes(1);
    expect(store.donnees).toEqual(DONNEES);
  });

  it("consigne une erreur explicite en cas d'échec, sans rien masquer", async () => {
    api.requete.mockRejectedValue(new api.ErreurApi("Accès refusé", 403));
    const store = useRolesStore();
    await store.charger();
    expect(store.donnees).toBeNull();
    expect(store.erreur).toBe("Accès refusé");
  });
});

describe("rolesPour()", () => {
  it("renvoie les rôles réels d'une permission connue", async () => {
    api.requete.mockResolvedValueOnce(DONNEES);
    const store = useRolesStore();
    await store.charger();
    expect(store.rolesPour("CONSULTER_TABLEAU_BORD")).toEqual(["administrateur", "responsable"]);
  });

  it("renvoie null (pas 'fermé à tous') pour une clé inconnue ou tant que non chargé", () => {
    const store = useRolesStore();
    expect(store.rolesPour("CLE_INEXISTANTE")).toBeNull();
    expect(store.rolesPour("CONSULTER_TABLEAU_BORD")).toBeNull(); // rien chargé encore
  });
});

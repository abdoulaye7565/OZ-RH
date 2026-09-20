import { createPinia, setActivePinia } from "pinia";
import { beforeEach, describe, expect, it, vi } from "vitest";

// Couvre modifier() (2026-09-09, voir docs/JOURNAL.md) — ajouté suite à un
// retour direct de l'utilisateur ("nous devons permettre la modification")
// pour compléter creer()/desactiver()/activer(), déjà couverts côté backend
// (tests/test_auth.py) mais jamais côté store.

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
const { useUtilisateursStore } = await import("./utilisateurs");

beforeEach(() => {
  setActivePinia(createPinia());
  vi.clearAllMocks();
});

describe("modifier()", () => {
  it("appelle PATCH sur la bonne route et remplace l'utilisateur dans la liste", async () => {
    const store = useUtilisateursStore();
    store.liste = [
      { id: 1, nom: "Ancien", prenom: "Nom", role: "technicien", site_id: null, courriel: null, actif: true },
      { id: 2, nom: "Autre", prenom: "Compte", role: "responsable", site_id: null, courriel: null, actif: true },
    ];
    const utilisateurModifie = { id: 1, nom: "Nouveau", prenom: "Nom", role: "responsable", site_id: 3, courriel: "x@y.z", actif: true };
    api.requete.mockResolvedValue(utilisateurModifie);

    const resultat = await store.modifier(1, { nom: "Nouveau", role: "responsable", site_id: 3, courriel: "x@y.z" });

    expect(api.requete).toHaveBeenCalledWith("/api/v1/auth/utilisateurs/1", {
      methode: "PATCH",
      corps: { nom: "Nouveau", role: "responsable", site_id: 3, courriel: "x@y.z" },
    });
    expect(resultat).toEqual(utilisateurModifie);
    expect(store.liste[0]).toEqual(utilisateurModifie);
    expect(store.liste[1].id).toBe(2); // l'autre compte n'est pas affecté
  });

  it("un refus serveur (ex. auto-rétrogradation) remonte sans modifier la liste locale", async () => {
    const store = useUtilisateursStore();
    const original = { id: 1, nom: "Admin", prenom: "Un", role: "administrateur", site_id: null, courriel: null, actif: true };
    store.liste = [original];
    api.requete.mockRejectedValue(new api.ErreurApi("Vous ne pouvez pas retirer votre propre rôle d'administrateur", 400));

    await expect(store.modifier(1, { role: "technicien" })).rejects.toMatchObject({ statut: 400 });
    expect(store.liste[0]).toEqual(original);
  });
});

import "fake-indexeddb/auto";
import { createPinia, setActivePinia } from "pinia";
import { beforeEach, describe, expect, it, vi } from "vitest";

// Couvre le mécanisme le plus complexe construit le 2026-09-09 (voir
// docs/JOURNAL.md, "Points critiques" point 4) : contrairement à
// Signalements et SLAM, une inspection est un flux en plusieurs étapes
// dépendantes côté serveur (créer → coter des points, plusieurs fois →
// clôturer). Ces tests vérifient qu'un seul élément reste en file par
// inspection (remplacé, jamais dupliqué) et que le bon `id`/`donnees_creation`
// est envoyé à la synchronisation selon que l'inspection a ou non déjà un id
// serveur réel.

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
const { useInspectionsStore } = await import("./inspections");
const filesync = await import("../services/filesync");

beforeEach(async () => {
  setActivePinia(createPinia());
  vi.clearAllMocks();
  // Même stratégie de nettoyage que filesync.test.js : vider le magasin
  // plutôt que supprimer la base (connexion mise en cache au niveau module).
  const base = await new Promise((resoudre, rejeter) => {
    const requete = indexedDB.open("sheq_hors_connexion", 1);
    requete.onupgradeneeded = () => {
      const b = requete.result;
      if (!b.objectStoreNames.contains("file_attente")) {
        b.createObjectStore("file_attente", { keyPath: "id", autoIncrement: true }).createIndex("type", "type", {
          unique: false,
        });
      }
    };
    requete.onsuccess = () => resoudre(requete.result);
    requete.onerror = () => rejeter(requete.error);
  });
  await new Promise((resoudre, rejeter) => {
    const tx = base.transaction("file_attente", "readwrite");
    tx.objectStore("file_attente").clear();
    tx.oncomplete = () => resoudre();
    tx.onerror = () => rejeter(tx.error);
  });
  base.close();
});

const DONNEES_CREATION = {
  modele: "incendie",
  site_id: 1,
  equipement_id: null,
  points: [{ point_checklist_id: 1, cotation: "C", observation: null }],
};

describe("creer() hors ligne — une inspection jamais créée côté serveur", () => {
  it("place l'inspection en file avec id=null (encore à créer) et donnees_creation", async () => {
    api.requete.mockRejectedValue(new TypeError("Failed to fetch"));
    const store = useInspectionsStore();

    const resultat = await store.creer(DONNEES_CREATION);

    expect(resultat.id).toMatch(/^local-/);
    expect(resultat.enAttente).toBe(true);
    const enAttente = await filesync.listerEnAttente();
    expect(enAttente).toHaveLength(1);
    expect(enAttente[0].champs).toMatchObject({ id: null, donnees_creation: DONNEES_CREATION });
  });

  it("un deuxième point coté (mettreAJourPoints) REMPLACE l'élément en file, n'en ajoute pas un second", async () => {
    api.requete.mockRejectedValue(new TypeError("Failed to fetch"));
    const store = useInspectionsStore();
    await store.creer(DONNEES_CREATION);

    const pointsMisAJour = [
      { point_checklist_id: 1, cotation: "C", observation: null },
      { point_checklist_id: 2, cotation: "NC", observation: "Extincteur vide" },
    ];
    await store.mettreAJourPoints(store.inspection.id, pointsMisAJour);

    const enAttente = await filesync.listerEnAttente();
    expect(enAttente).toHaveLength(1); // toujours un seul élément
    expect(enAttente[0].champs.points).toEqual(pointsMisAJour);
    expect(enAttente[0].champs.id).toBeNull(); // toujours "pas encore créée"
    expect(store.inspection.points).toEqual(pointsMisAJour);
  });

  it("clôturer hors ligne met à jour le même élément en file avec cloturer=true", async () => {
    api.requete.mockRejectedValue(new TypeError("Failed to fetch"));
    const store = useInspectionsStore();
    await store.creer(DONNEES_CREATION);

    await store.cloturer(store.inspection.id);

    const enAttente = await filesync.listerEnAttente();
    expect(enAttente).toHaveLength(1);
    expect(enAttente[0].champs.cloturer).toBe(true);
    expect(enAttente[0].champs.donnees_creation).toMatchObject({ modele: "incendie" });
    expect(store.inspection.statut).toBe("cloturee");
  });
});

describe("mettreAJourPoints()/cloturer() hors ligne — une inspection déjà réelle côté serveur", () => {
  it("une inspection créée EN LIGNE puis coupée hors ligne met en file avec le vrai id, pas de donnees_creation", async () => {
    api.requete.mockResolvedValueOnce({ id: 42, modele: "incendie", site_id: 1, statut: "en_cours", points: [] });
    const store = useInspectionsStore();
    await store.creer(DONNEES_CREATION); // réussit en ligne : id réel 42

    api.requete.mockRejectedValue(new TypeError("Failed to fetch")); // réseau tombe ensuite
    const pointsMisAJour = [{ point_checklist_id: 1, cotation: "NC", observation: null }];
    await store.mettreAJourPoints(42, pointsMisAJour);

    expect(store.inspection.id).toBe(42); // pas de faux id local : l'id réel existe déjà
    const enAttente = await filesync.listerEnAttente();
    expect(enAttente).toHaveLength(1);
    expect(enAttente[0].champs).toMatchObject({ id: 42, donnees_creation: null, points: pointsMisAJour });
  });
});

describe("getters de restitution — quel équipement, où, par qui (2026-09-10)", () => {
  it("nomEquipement() renvoie code d'inventaire + marque/modèle", () => {
    const store = useInspectionsStore();
    store.equipements = [{ id: 1, identity: "BKO-AP-01", marque: "MikroTik", modele: "hAP ac2", emplacement: "Local technique" }];
    expect(store.nomEquipement(1)).toBe("BKO-AP-01 — MikroTik hAP ac2");
  });

  it("nomEquipement() renvoie null pour un id inconnu", () => {
    const store = useInspectionsStore();
    store.equipements = [];
    expect(store.nomEquipement(999)).toBeNull();
  });

  it("nomEquipement() tombe sur la seule identity si marque/modèle absents", () => {
    const store = useInspectionsStore();
    store.equipements = [{ id: 2, identity: "BKO-SW-02" }];
    expect(store.nomEquipement(2)).toBe("BKO-SW-02");
  });

  it("equipementParId() renvoie l'objet complet", () => {
    const store = useInspectionsStore();
    const eq = { id: 3, identity: "BKO-RT-03", site_id: 1 };
    store.equipements = [eq];
    expect(store.equipementParId(3)).toEqual(eq);
    expect(store.equipementParId(4)).toBeNull();
  });
});

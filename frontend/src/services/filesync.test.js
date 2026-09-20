import "fake-indexeddb/auto";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { reactive } from "vue";
import * as filesync from "./filesync";

// IndexedDB n'existe pas dans jsdom : fake-indexeddb fournit une implémentation
// en mémoire suffisante pour tester la logique de file (ordre, comptage,
// branchement succès/échec/réseau de synchroniser()) — voir docs/JOURNAL.md,
// "Points critiques", point 5. Ne prouve PAS qu'un DataCloneError se
// reproduirait ici comme dans un vrai navigateur (fake-indexeddb n'a aucune
// raison de partager les mêmes restrictions de clonage qu'un moteur JS de
// navigateur) : le test ci-dessous vérifie l'invariant qui compte
// réellement — qu'après ajouterEnAttente(), les données stockées sont des
// objets/tableaux plats, indépendants de toute réactivité Vue, à n'importe
// quelle profondeur — pas qu'une erreur précise se produit ou non ici.

// filesync.js garde sa connexion IndexedDB ouverte au niveau du module (une
// seule fois pour toute la durée de l'app, par design) : indexedDB.
// deleteDatabase() reste bloqué (onblocked) tant qu'une connexion existe déjà
// et ne se ferme jamais entre deux tests de ce fichier — ne pas l'utiliser
// ici. On vide plutôt le magasin via une connexion ordinaire à la même base :
// ouvrir à la même version ne redéclenche pas onupgradeneeded une fois le
// magasin déjà créé, donc pas de conflit de schéma avec filesync.js.
beforeEach(async () => {
  const base = await new Promise((resoudre, rejeter) => {
    const requete = indexedDB.open("sheq_hors_connexion", 1);
    requete.onupgradeneeded = () => {
      const b = requete.result;
      if (!b.objectStoreNames.contains("file_attente")) {
        const magasin = b.createObjectStore("file_attente", { keyPath: "id", autoIncrement: true });
        magasin.createIndex("type", "type", { unique: false });
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

describe("ajouterEnAttente / listerEnAttente / compterEnAttente", () => {
  it("range un élément et lui attribue une référence locale", async () => {
    const element = await filesync.ajouterEnAttente("signalement", { lieu: "Pylône P-1" }, []);
    expect(element.id).toBeTypeOf("number");
    expect(element.referenceLocale).toBe(`LOCAL-${element.id}`);
    expect(element.tentatives).toBe(0);
  });

  it("liste les éléments dans l'ordre de saisie (le plus ancien en premier)", async () => {
    await filesync.ajouterEnAttente("signalement", { lieu: "Premier" }, []);
    await filesync.ajouterEnAttente("signalement", { lieu: "Deuxième" }, []);
    await filesync.ajouterEnAttente("signalement", { lieu: "Troisième" }, []);

    const liste = await filesync.listerEnAttente();
    expect(liste.map((e) => e.champs.lieu)).toEqual(["Premier", "Deuxième", "Troisième"]);
  });

  it("compte correctement, y compris à zéro", async () => {
    expect(await filesync.compterEnAttente()).toBe(0);
    await filesync.ajouterEnAttente("signalement", {}, []);
    expect(await filesync.compterEnAttente()).toBe(1);
  });

  it("copie champs/fichiers en objets plats (pas de référence conservée vers l'original)", async () => {
    const champsOriginaux = { lieu: "Pylône P-1" };
    const fichiersOriginaux = [];
    const element = await filesync.ajouterEnAttente("signalement", champsOriginaux, fichiersOriginaux);

    champsOriginaux.lieu = "Modifié après coup";
    expect(element.champs.lieu).toBe("Pylône P-1");
  });

  it("dérobotise aussi une valeur RÉACTIVE IMBRIQUÉE, pas seulement le conteneur (régression SLAM, 2026-09-09)", async () => {
    // Reproduit exactement la forme de stores/signalements.js et
    // SlamView.vue : `champs` est un objet plat, mais l'une de ses valeurs
    // est elle-même un ref()/reactive() Vue — { ...champs } (copie
    // superficielle) ne "dérobotise" pas cette valeur-là, seulement le
    // conteneur de premier niveau. Un JSON.parse(JSON.stringify(...)) le
    // fait à n'importe quelle profondeur.
    const etapesValidees = reactive([
      [true, true, false, true],
      [false, false, false, false],
    ]);
    const champs = { decision: "GO", etapes_validees: etapesValidees };

    const element = await filesync.ajouterEnAttente("slam", champs, []);

    expect(element.champs.etapes_validees).toEqual([
      [true, true, false, true],
      [false, false, false, false],
    ]);
    // Pas seulement un contenu identique : une vraie copie plate, insensible
    // à Vue — vérifié en modifiant l'original après coup.
    etapesValidees[0][0] = false;
    expect(element.champs.etapes_validees[0][0]).toBe(true);

    const relu = (await filesync.listerEnAttente())[0];
    expect(relu.champs.etapes_validees).toEqual([
      [true, true, false, true],
      [false, false, false, false],
    ]);
  });
});

describe("synchroniser()", () => {
  it("rejoue les éléments dans l'ordre, retire ceux qui réussissent, appelle onSucces une fois par type", async () => {
    await filesync.ajouterEnAttente("signalement", { lieu: "A" }, []);
    await filesync.ajouterEnAttente("signalement", { lieu: "B" }, []);

    const ordreExecute = [];
    const onSucces = vi.fn();
    const resultat = await filesync.synchroniser({
      signalement: {
        executer: async (champs) => {
          ordreExecute.push(champs.lieu);
        },
        onSucces,
      },
    });

    expect(ordreExecute).toEqual(["A", "B"]);
    expect(resultat).toEqual({ reussis: 2, echoues: 0 });
    expect(onSucces).toHaveBeenCalledTimes(1); // une fois par type concerné, pas une fois par élément
    expect(await filesync.compterEnAttente()).toBe(0);
  });

  it("un vrai refus (pas une erreur réseau) reste en file, incrémente tentatives, et n'empêche pas la suite", async () => {
    await filesync.ajouterEnAttente("signalement", { lieu: "Refusé" }, []);
    await filesync.ajouterEnAttente("signalement", { lieu: "Accepté ensuite" }, []);

    const resultat = await filesync.synchroniser({
      signalement: {
        executer: async (champs) => {
          if (champs.lieu === "Refusé") throw new Error("422 : lieu déjà utilisé");
        },
      },
    });

    expect(resultat).toEqual({ reussis: 1, echoues: 1 });
    const restants = await filesync.listerEnAttente();
    expect(restants).toHaveLength(1);
    expect(restants[0].champs.lieu).toBe("Refusé");
    expect(restants[0].tentatives).toBe(1);
    expect(restants[0].derniereErreur).toBe("422 : lieu déjà utilisé");
  });

  it("une erreur réseau (TypeError) arrête la file immédiatement, sans pénaliser l'élément ni les suivants", async () => {
    await filesync.ajouterEnAttente("signalement", { lieu: "Un" }, []);
    await filesync.ajouterEnAttente("signalement", { lieu: "Deux" }, []);

    const executer = vi.fn(async () => {
      throw new TypeError("Failed to fetch");
    });
    const resultat = await filesync.synchroniser({ signalement: { executer } });

    expect(resultat).toEqual({ reussis: 0, echoues: 0 });
    expect(executer).toHaveBeenCalledTimes(1); // jamais tenté le deuxième élément
    const restants = await filesync.listerEnAttente();
    expect(restants).toHaveLength(2);
    expect(restants[0].tentatives).toBe(0); // pas compté comme un échec
  });

  it("un type sans gestionnaire enregistré reste en file, silencieusement", async () => {
    await filesync.ajouterEnAttente("slam", { etape: 1 }, []);

    const resultat = await filesync.synchroniser({});

    expect(resultat).toEqual({ reussis: 0, echoues: 0 });
    expect(await filesync.compterEnAttente()).toBe(1);
  });
});

/**
 * File d'attente de synchronisation hors connexion (mécanisme annoncé mais
 * jamais construit jusqu'ici — voir le commentaire de BandeauReseau.vue).
 *
 * Principe (CLAUDE.md, contrainte fondatrice n°1 ; CDC §7 point 7, "numéro
 * attribué à la synchronisation, pas à la saisie hors ligne") : quand une
 * écriture échoue parce que le réseau est indisponible, on la range dans
 * IndexedDB avec une référence provisoire locale au lieu de la perdre ou de
 * bloquer l'utilisateur. Au retour du réseau, chaque élément est rejoué vers
 * l'API dans l'ordre où il a été saisi.
 *
 * Générique par construction (pas seulement pour les signalements) : chaque
 * module concerné (signalements en premier, puis SLAM et inspections)
 * enregistre son propre "gestionnaire" — comment rejouer un élément de son
 * type — via horsConnexion.enregistrerGestionnaire().
 *
 * Aucune dépendance ajoutée : IndexedDB est une API native du navigateur.
 */

const NOM_BASE = "sheq_hors_connexion";
const VERSION_BASE = 1;
const MAGASIN = "file_attente";

let promesseBase = null;

function ouvrirBase() {
  if (promesseBase) return promesseBase;
  promesseBase = new Promise((resoudre, rejeter) => {
    const requete = indexedDB.open(NOM_BASE, VERSION_BASE);
    requete.onupgradeneeded = () => {
      const base = requete.result;
      if (!base.objectStoreNames.contains(MAGASIN)) {
        const magasin = base.createObjectStore(MAGASIN, { keyPath: "id", autoIncrement: true });
        magasin.createIndex("type", "type", { unique: false });
      }
    };
    requete.onsuccess = () => resoudre(requete.result);
    requete.onerror = () => rejeter(requete.error);
  });
  return promesseBase;
}

async function transaction(mode) {
  const base = await ouvrirBase();
  const tx = base.transaction(MAGASIN, mode);
  return { tx, magasin: tx.objectStore(MAGASIN) };
}

/**
 * Range un élément en attente. `champs` est l'objet à renvoyer tel quel au
 * gestionnaire du type au moment du rejeu ; `fichiers` (optionnel) est
 * stocké tel quel — IndexedDB clone nativement les File/Blob, pas besoin de
 * les encoder.
 */
export async function ajouterEnAttente(type, champs, fichiers = []) {
  const { tx, magasin } = await transaction("readwrite");
  const enregistrement = {
    type,
    // `champs` vient typiquement d'un ref()/reactive() Vue (Proxy), qu'IndexedDB
    // ne sait pas cloner (DataCloneError, "[object Array] could not be
    // cloned"). Une copie superficielle (`{ ...champs }`) ne suffit PAS dès
    // que `champs` contient une valeur imbriquée elle-même réactive (ex.
    // SLAM : `etapes_validees` est un tableau de tableaux de booléens, ref()
    // à part entière) — bug réel trouvé le 2026-09-09 en testant le SLAM
    // hors connexion, une deuxième fois après celui des signalements la
    // veille : un clonage structuré JSON, récursif par nature, retire toute
    // réactivité à n'importe quelle profondeur. Ne fonctionnerait pas pour
    // des valeurs non sérialisables (Date, Map...) mais tout ce qui transite
    // ici part de toute façon en JSON vers l'API — jamais de File/Blob dans
    // `champs`, ceux-là vivent exclusivement dans `fichiers`.
    champs: JSON.parse(JSON.stringify(champs)),
    // Les fichiers eux-mêmes ne sont jamais rendus réactifs par Vue (seul le
    // tableau qui les contient l'est) : Array.from() suffit à en sortir.
    fichiers: Array.from(fichiers ?? []),
    dateCreation: new Date().toISOString(),
    tentatives: 0,
    derniereErreur: null,
  };
  return new Promise((resoudre, rejeter) => {
    const requete = magasin.add(enregistrement);
    requete.onsuccess = () => resoudre({ ...enregistrement, id: requete.result, referenceLocale: `LOCAL-${requete.result}` });
    requete.onerror = () => rejeter(requete.error);
    tx.onerror = () => rejeter(tx.error);
  });
}

export async function listerEnAttente() {
  const { magasin } = await transaction("readonly");
  return new Promise((resoudre, rejeter) => {
    const requete = magasin.getAll();
    requete.onsuccess = () => resoudre(requete.result.sort((a, b) => a.id - b.id));
    requete.onerror = () => rejeter(requete.error);
  });
}

export async function compterEnAttente() {
  const { magasin } = await transaction("readonly");
  return new Promise((resoudre, rejeter) => {
    const requete = magasin.count();
    requete.onsuccess = () => resoudre(requete.result);
    requete.onerror = () => rejeter(requete.error);
  });
}

/**
 * Remplace les `champs` d'un élément déjà en file, sans en créer un nouveau.
 * Ajouté pour Inspections (2026-09-09) : contrairement à un signalement ou
 * une décision SLAM (un seul envoi, terminé), une inspection saisie hors
 * connexion évolue point par point pendant toute sa durée — sans ceci,
 * chaque coche créerait un nouvel élément en file, et la synchronisation les
 * rejouerait tous dans l'ordre au lieu de n'envoyer que le dernier état
 * (déjà complet à chaque fois, voir stores/inspections.js).
 */
export async function mettreAJourEnAttente(id, champs) {
  const { tx, magasin } = await transaction("readwrite");
  return new Promise((resoudre, rejeter) => {
    const lecture = magasin.get(id);
    lecture.onsuccess = () => {
      const enregistrement = lecture.result;
      if (!enregistrement) return rejeter(new Error(`Élément en attente introuvable (id ${id})`));
      enregistrement.champs = JSON.parse(JSON.stringify(champs));
      const ecriture = magasin.put(enregistrement);
      ecriture.onsuccess = () => resoudre(enregistrement);
      ecriture.onerror = () => rejeter(ecriture.error);
    };
    lecture.onerror = () => rejeter(lecture.error);
    tx.onerror = () => rejeter(tx.error);
  });
}

async function supprimerEnAttente(id) {
  const { magasin } = await transaction("readwrite");
  return new Promise((resoudre, rejeter) => {
    const requete = magasin.delete(id);
    requete.onsuccess = () => resoudre();
    requete.onerror = () => rejeter(requete.error);
  });
}

async function enregistrerEchec(id, message) {
  const { tx, magasin } = await transaction("readwrite");
  return new Promise((resoudre, rejeter) => {
    const lecture = magasin.get(id);
    lecture.onsuccess = () => {
      const enregistrement = lecture.result;
      if (!enregistrement) return resoudre();
      enregistrement.tentatives += 1;
      enregistrement.derniereErreur = message;
      const ecriture = magasin.put(enregistrement);
      ecriture.onsuccess = () => resoudre();
      ecriture.onerror = () => rejeter(ecriture.error);
    };
    lecture.onerror = () => rejeter(lecture.error);
    tx.onerror = () => rejeter(tx.error);
  });
}

// Une erreur réseau (fetch qui ne peut même pas joindre le serveur) diffère
// d'un vrai refus serveur (422, 401…) : la première signifie "on est encore
// hors connexion, on réessaiera plus tard" et ne doit pas compter comme un
// échec de l'élément ; la seconde est un vrai problème à signaler.
function estErreurReseau(e) {
  return e instanceof TypeError;
}

/**
 * Rejoue tous les éléments en attente, dans l'ordre de saisie. `gestionnaires`
 * associe un type à `{ executer(champs, fichiers), onSucces }`.
 *
 * S'arrête dès qu'une erreur réseau survient (on est probablement retombé
 * hors ligne en cours de route) plutôt que de marquer en échec tout le reste
 * de la file. Un vrai refus serveur, lui, est enregistré sur l'élément
 * concerné et n'empêche pas la suite de la file d'être rejouée.
 */
export async function synchroniser(gestionnaires) {
  const enAttente = await listerEnAttente();
  const typesReussis = new Set();
  let reussis = 0;
  let echoues = 0;

  for (const element of enAttente) {
    const gestionnaire = gestionnaires[element.type];
    if (!gestionnaire) continue; // type sans gestionnaire enregistré (module pas encore branché)

    try {
      await gestionnaire.executer(element.champs, element.fichiers);
      await supprimerEnAttente(element.id);
      reussis += 1;
      typesReussis.add(element.type);
    } catch (e) {
      if (estErreurReseau(e)) break; // on est de nouveau hors ligne : on s'arrête là, sans pénaliser cet élément
      await enregistrerEchec(element.id, e?.message ?? "Échec de synchronisation");
      echoues += 1;
    }
  }

  for (const type of typesReussis) {
    await gestionnaires[type].onSucces?.();
  }

  return { reussis, echoues };
}

export default { ajouterEnAttente, listerEnAttente, compterEnAttente, mettreAJourEnAttente, synchroniser };

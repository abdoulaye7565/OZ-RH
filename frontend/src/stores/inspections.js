import { defineStore } from "pinia";
import api from "../services/api";
import { useHorsConnexionStore } from "./horsConnexion";

export const TYPES_INSPECTION = [
  { valeur: "locaux", libelle: "Locaux et postes de travail", abrege: "Locaux" },
  { valeur: "incendie", libelle: "Incendie et extincteurs", abrege: "Incendie" },
  { valeur: "electricite", libelle: "Installations électriques", abrege: "Électricité" },
  { valeur: "installations", libelle: "Installations en hauteur", abrege: "Hauteur" },
  { valeur: "equipements", libelle: "Équipements", abrege: "Équipements" },
];

// Mode hors connexion (2026-09-09, voir docs/JOURNAL.md "Points critiques"
// point 4) : contrairement à Signalements et SLAM (une saisie, un envoi,
// terminé), une inspection est un flux en plusieurs étapes dépendantes côté
// serveur (créer → coter des points, potentiellement plusieurs fois → clôturer)
// — exactement le scénario où le réseau manque le plus (cocher des points en
// marchant sur le site). Simplification décisive : PATCH /points envoie déjà
// l'état COMPLET des réponses à chaque fois (pas un patch incrémental, voir
// le commentaire de InspectionDetailView.vue) — donc pas besoin d'accumuler
// des opérations en file, juste de garder UN SEUL élément par inspection et
// de le remplacer à chaque coche (horsConnexion.mettreAJourEnAttente).
const CLE_CACHE_REFERENTIELS = "sheq_inspections_referentiels_cache";
const clePointsCache = (modele) => `sheq_inspections_points_cache_${modele}`;

function lireCache(cle) {
  try {
    const brut = localStorage.getItem(cle);
    return brut ? JSON.parse(brut) : null;
  } catch {
    return null;
  }
}

function ecrireCache(cle, valeur) {
  try {
    localStorage.setItem(cle, JSON.stringify(valeur));
  } catch {
    // Stockage indisponible : le cache ne survit simplement pas, pas bloquant.
  }
}

function estLocal(id) {
  return typeof id === "string" && id.startsWith("local-");
}

export const useInspectionsStore = defineStore("inspections", {
  state: () => ({
    liste: [],
    planification: [],
    sites: [],
    equipements: [],
    utilisateurs: [],
    inspection: null, // inspection en cours de saisie / consultée en détail
    pointsChecklist: [], // référentiel du modèle choisi (id + libellé)
    chargement: false,
    erreur: null,
  }),

  getters: {
    nomSite: (state) => (id) => state.sites.find((s) => s.id === id)?.nom ?? null,
    nomUtilisateur: (state) => (id) => {
      const u = state.utilisateurs.find((u) => u.id === id);
      return u ? `${u.prenom} ${u.nom}` : null;
    },
    equipementParId: (state) => (id) => state.equipements.find((e) => e.id === id) ?? null,
    // Libellé lisible d'un équipement inspecté : code d'inventaire (identity)
    // + marque/modèle, tel qu'affiché dans le Parc — sans ça, la question
    // "quel équipement a été inspecté" ne trouve qu'un `equipement_id` brut.
    nomEquipement: (state) => (id) => {
      const e = state.equipements.find((eq) => eq.id === id);
      if (!e) return null;
      const details = [e.marque, e.modele].filter(Boolean).join(" ");
      return details ? `${e.identity} — ${details}` : e.identity;
    },
    libelleType: () => (valeur) => TYPES_INSPECTION.find((t) => t.valeur === valeur)?.libelle ?? valeur,
    // Conformité moyenne par type, calculée côté client à partir des
    // inspections clôturées — aucune route d'agrégation dédiée côté API.
    // `taux_conformite` (API) est une fraction 0-1 (Inspection.taux_conformite,
    // conformes / total) : converti ici en pourcentage 0-100, seule unité
    // utilisée côté affichage (barres, tableaux).
    tauxParType: (state) => {
      const totaux = {};
      for (const insp of state.liste) {
        if (insp.taux_conformite === null || insp.taux_conformite === undefined) continue;
        totaux[insp.modele] ??= { somme: 0, n: 0 };
        totaux[insp.modele].somme += insp.taux_conformite * 100;
        totaux[insp.modele].n += 1;
      }
      const moyennes = {};
      for (const [modele, { somme, n }] of Object.entries(totaux)) moyennes[modele] = somme / n;
      return moyennes;
    },
  },

  actions: {
    async charger() {
      this.chargement = true;
      this.erreur = null;
      try {
        const [liste, planification, sites, equipements, utilisateurs] = await Promise.all([
          api.requete("/api/v1/inspections"),
          api.requete("/api/v1/inspections/planification"),
          api.requete("/api/v1/sites"),
          api.requete("/api/v1/equipements"),
          api.requete("/api/v1/auth/utilisateurs"),
        ]);
        this.liste = liste;
        this.planification = planification;
        this.sites = sites;
        this.equipements = equipements;
        this.utilisateurs = utilisateurs;
      } catch (e) {
        this.erreur = e instanceof api.ErreurApi ? e.message : "Impossible de charger les inspections";
      } finally {
        this.chargement = false;
      }
    },

    // Référentiel des points d'un modèle : mis en cache dès qu'il charge avec
    // succès, utilisé hors ligne si le réseau manque — même principe que le
    // référentiel SLAM (voir SlamView.vue). Sans lui, impossible de démarrer
    // une inspection déjà hors ligne dès l'ouverture de l'écran.
    async chargerPoints(modele) {
      try {
        this.pointsChecklist = await api.requete(`/api/v1/points-checklist?type_inspection=${modele}`);
        ecrireCache(clePointsCache(modele), this.pointsChecklist);
      } catch (e) {
        const cache = lireCache(clePointsCache(modele));
        if (e instanceof TypeError && cache) {
          this.pointsChecklist = cache;
        } else {
          throw e;
        }
      }
    },

    // Charge sites/équipements/utilisateurs seulement s'ils ne le sont pas
    // déjà — nécessaire quand la fiche de saisie (InspectionDetailView) est
    // atteinte directement (lien profond, rechargement de page) sans passer
    // par l'écran de liste, dont le onMounted les charge normalement. Mis en
    // cache et utilisé hors ligne, même principe que chargerPoints().
    async chargerReferentielsSiBesoin() {
      if (this.sites.length) return;
      try {
        const [sites, equipements, utilisateurs] = await Promise.all([
          api.requete("/api/v1/sites"),
          api.requete("/api/v1/equipements"),
          api.requete("/api/v1/auth/utilisateurs"),
        ]);
        this.sites = sites;
        this.equipements = equipements;
        this.utilisateurs = utilisateurs;
        ecrireCache(CLE_CACHE_REFERENTIELS, { sites, equipements, utilisateurs });
      } catch (e) {
        const cache = lireCache(CLE_CACHE_REFERENTIELS);
        if (e instanceof TypeError && cache) {
          this.sites = cache.sites;
          this.equipements = cache.equipements;
          this.utilisateurs = cache.utilisateurs;
        } else {
          throw e;
        }
      }
    },

    // Consulter une inspection déjà réelle (id serveur connu) exige le
    // réseau — hors périmètre de ce chantier, qui vise la SAISIE sur site,
    // pas la consultation ultérieure d'une fiche déjà synchronisée.
    async chargerInspection(id) {
      this.inspection = await api.requete(`/api/v1/inspections/${id}`);
      await this.chargerPoints(this.inspection.modele);
      return this.inspection;
    },

    async creer(donnees) {
      try {
        const inspection = await api.requete("/api/v1/inspections", { methode: "POST", corps: donnees });
        this.inspection = inspection;
        return inspection;
      } catch (e) {
        if (!(e instanceof TypeError)) throw e;
        this.inspection = {
          id: null, // résolu par _mettreEnFile() ci-dessous (id: null → pas encore créée)
          modele: donnees.modele,
          site_id: donnees.site_id,
          equipement_id: donnees.equipement_id ?? null,
          objet_inspecte: donnees.objet_inspecte ?? null,
          statut: "en_cours",
          points: donnees.points,
          _donneesCreation: donnees,
        };
        return this._mettreEnFile(donnees.points, false);
      }
    },

    async mettreAJourPoints(id, points) {
      if (estLocal(id)) return this._mettreEnFile(points, false);
      try {
        this.inspection = await api.requete(`/api/v1/inspections/${id}/points`, { methode: "PATCH", corps: { points } });
        return this.inspection;
      } catch (e) {
        if (!(e instanceof TypeError)) throw e;
        return this._mettreEnFile(points, false, id);
      }
    },

    async cloturer(id) {
      if (estLocal(id)) return this._mettreEnFile(this.inspection?.points ?? null, true);
      try {
        this.inspection = await api.requete(`/api/v1/inspections/${id}/cloturer`, { methode: "POST" });
        const i = this.liste.findIndex((x) => x.id === id);
        if (i !== -1) this.liste[i] = this.inspection;
        else this.liste.unshift(this.inspection);
        return this.inspection;
      } catch (e) {
        if (!(e instanceof TypeError)) throw e;
        return this._mettreEnFile(null, true, id);
      }
    },

    /**
     * Cœur du mécanisme hors connexion de ce module. Un seul élément en file
     * par inspection, remplacé (pas dupliqué) à chaque coche — voir le
     * commentaire d'en-tête du fichier. `id` reste `null` tant que
     * l'inspection n'a jamais été créée côté serveur (donnees_creation
     * porte alors ce qu'il faut pour le POST initial à la synchronisation) ;
     * une fois `id` réel connu, seuls points/cloturer sont encore à envoyer.
     */
    async _mettreEnFile(points, cloturer, idReelConnu = null) {
      const horsConnexion = useHorsConnexionStore();
      // `_donneesCreation` reste posé pour toute la session locale dès
      // qu'une inspection est née hors ligne — pas de re-test sur `id`, qui
      // lui change dès la première mise en file (résolu en `local-N`) alors
      // que la création côté serveur, elle, n'a toujours pas eu lieu.
      const pasEncoreCreee = Boolean(this.inspection?._donneesCreation);
      const champs = {
        id: pasEncoreCreee ? null : (idReelConnu ?? this.inspection?.id ?? null),
        donnees_creation: pasEncoreCreee ? this.inspection._donneesCreation : null,
        points: points ?? this.inspection?.points ?? [],
        cloturer: cloturer || this.inspection?.statut === "cloturee",
      };

      if (this.inspection?._idEnAttente) {
        await horsConnexion.mettreAJourEnAttente(this.inspection._idEnAttente, champs);
      } else {
        const element = await horsConnexion.ajouterEnAttente("inspection", champs, []);
        this.inspection = {
          ...this.inspection,
          id: this.inspection?.id ?? `local-${element.id}`,
          _idEnAttente: element.id,
        };
      }

      if (points) this.inspection.points = points;
      if (cloturer) this.inspection.statut = "cloturee";
      this.inspection.enAttente = true;
      return this.inspection;
    },
  },
});

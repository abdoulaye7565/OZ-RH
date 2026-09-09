import { defineStore } from "pinia";
import api from "../services/api";

export const TYPES_INSPECTION = [
  { valeur: "locaux", libelle: "Locaux et postes de travail", abrege: "Locaux" },
  { valeur: "incendie", libelle: "Incendie et extincteurs", abrege: "Incendie" },
  { valeur: "electricite", libelle: "Installations électriques", abrege: "Électricité" },
  { valeur: "installations", libelle: "Installations en hauteur", abrege: "Hauteur" },
  { valeur: "equipements", libelle: "Équipements", abrege: "Équipements" },
];

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

    async chargerPoints(modele) {
      this.pointsChecklist = await api.requete(`/api/v1/points-checklist?type_inspection=${modele}`);
    },

    // Charge sites/équipements/utilisateurs seulement s'ils ne le sont pas
    // déjà — nécessaire quand la fiche de saisie (InspectionDetailView) est
    // atteinte directement (lien profond, rechargement de page) sans passer
    // par l'écran de liste, dont le onMounted les charge normalement.
    async chargerReferentielsSiBesoin() {
      if (this.sites.length) return;
      const [sites, equipements, utilisateurs] = await Promise.all([
        api.requete("/api/v1/sites"),
        api.requete("/api/v1/equipements"),
        api.requete("/api/v1/auth/utilisateurs"),
      ]);
      this.sites = sites;
      this.equipements = equipements;
      this.utilisateurs = utilisateurs;
    },

    async chargerInspection(id) {
      this.inspection = await api.requete(`/api/v1/inspections/${id}`);
      await this.chargerPoints(this.inspection.modele);
      return this.inspection;
    },

    async creer(donnees) {
      const inspection = await api.requete("/api/v1/inspections", { methode: "POST", corps: donnees });
      this.inspection = inspection;
      return inspection;
    },

    async mettreAJourPoints(id, points) {
      this.inspection = await api.requete(`/api/v1/inspections/${id}/points`, { methode: "PATCH", corps: { points } });
      return this.inspection;
    },

    async cloturer(id) {
      this.inspection = await api.requete(`/api/v1/inspections/${id}/cloturer`, { methode: "POST" });
      const i = this.liste.findIndex((x) => x.id === id);
      if (i !== -1) this.liste[i] = this.inspection;
      else this.liste.unshift(this.inspection);
      return this.inspection;
    },
  },
});

import { defineStore } from "pinia";
import api from "../services/api";

// Gestion des sites (2026-09-10, retour direct de l'utilisateur : « on a un
// seul site alors que nous intervenons sur plusieurs sites »). La création se
// faisait jusqu'ici directement en base ; création / modification / archivage
// sont désormais exposés (réservés à l'administrateur côté serveur).

export const TYPES_SITE = [
  { valeur: "siege", libelle: "Siège" },
  { valeur: "client", libelle: "Site client" },
];

export const useSitesStore = defineStore("sites", {
  state: () => ({
    liste: [],
    chargement: false,
    erreur: null,
  }),

  getters: {
    libelleType: () => (valeur) => TYPES_SITE.find((t) => t.valeur === valeur)?.libelle ?? valeur,
  },

  actions: {
    async charger() {
      this.chargement = true;
      this.erreur = null;
      try {
        this.liste = await api.requete("/api/v1/sites");
      } catch (e) {
        this.erreur = e instanceof api.ErreurApi ? e.message : "Impossible de charger les sites";
      } finally {
        this.chargement = false;
      }
    },

    async creer(donnees) {
      const site = await api.requete("/api/v1/sites", { methode: "POST", corps: donnees });
      await this.charger();
      return site;
    },

    async modifier(id, donnees) {
      const site = await api.requete(`/api/v1/sites/${id}`, { methode: "PATCH", corps: donnees });
      const i = this.liste.findIndex((s) => s.id === id);
      if (i !== -1) this.liste[i] = site;
      return site;
    },

    // Le serveur refuse (409) tant qu'un équipement ou un permis en cours y est
    // rattaché — l'erreur remonte telle quelle à l'appelant.
    async archiver(id) {
      await api.requete(`/api/v1/sites/${id}/archiver`, { methode: "POST" });
      await this.charger();
    },
  },
});

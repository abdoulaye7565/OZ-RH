import { defineStore } from "pinia";
import api from "../services/api";

export const useDechetsStore = defineStore("dechets", {
  state: () => ({
    liste: [],
    sites: [],
    chargement: false,
    erreur: null,
  }),

  getters: {
    nomSite: (state) => (id) => state.sites.find((s) => s.id === id)?.nom ?? null,
    enStock: (state) => state.liste.filter((d) => !d.date_enlevement),
    enleves: (state) => state.liste.filter((d) => d.date_enlevement),
  },

  actions: {
    async charger() {
      this.chargement = true;
      this.erreur = null;
      try {
        const [liste, sites] = await Promise.all([api.requete("/api/v1/dechets"), api.requete("/api/v1/sites")]);
        this.liste = liste;
        this.sites = sites;
      } catch (e) {
        this.erreur = e instanceof api.ErreurApi ? e.message : "Impossible de charger le registre des déchets";
      } finally {
        this.chargement = false;
      }
    },

    async creer(donnees) {
      const dechet = await api.requete("/api/v1/dechets", { methode: "POST", corps: donnees });
      this.liste.unshift(dechet);
      return dechet;
    },

    async modifier(dechetId, donnees) {
      const mis_a_jour = await api.requete(`/api/v1/dechets/${dechetId}`, { methode: "PATCH", corps: donnees });
      const i = this.liste.findIndex((d) => d.id === dechetId);
      if (i !== -1) this.liste[i] = mis_a_jour;
      return mis_a_jour;
    },

    // Le serveur revérifie tout (point 9 CLAUDE.md) ; jamais de suppression.
    async archiver(dechetId) {
      await api.requete(`/api/v1/dechets/${dechetId}/archiver`, { methode: "POST" });
      await this.charger();
    },

    async enregistrerEnlevement(dechetId, dateEnlevement, justificatif) {
      const donnees = new FormData();
      donnees.set("date_enlevement", dateEnlevement);
      if (justificatif) donnees.set("justificatif", justificatif);
      const mis_a_jour = await api.requete(`/api/v1/dechets/${dechetId}/enlevement`, { methode: "POST", corps: donnees });
      const i = this.liste.findIndex((d) => d.id === dechetId);
      if (i !== -1) this.liste[i] = mis_a_jour;
      return mis_a_jour;
    },
  },
});

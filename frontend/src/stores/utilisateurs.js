import { defineStore } from "pinia";
import api from "../services/api";

export const useUtilisateursStore = defineStore("utilisateurs", {
  state: () => ({
    liste: [],
    sites: [],
    chargement: false,
    erreur: null,
  }),

  getters: {
    nomSite: (state) => (id) => state.sites.find((s) => s.id === id)?.nom ?? null,
    actifs: (state) => state.liste.filter((u) => u.actif),
    desactives: (state) => state.liste.filter((u) => !u.actif),
  },

  actions: {
    async charger() {
      this.chargement = true;
      this.erreur = null;
      try {
        const [liste, sites] = await Promise.all([api.requete("/api/v1/auth/utilisateurs"), api.requete("/api/v1/sites")]);
        this.liste = liste;
        this.sites = sites;
      } catch (e) {
        this.erreur = e instanceof api.ErreurApi ? e.message : "Impossible de charger les utilisateurs";
      } finally {
        this.chargement = false;
      }
    },

    async creer(donnees) {
      const utilisateur = await api.requete("/api/v1/auth/utilisateurs", { methode: "POST", corps: donnees });
      this.liste.unshift(utilisateur);
      return utilisateur;
    },

    async desactiver(id) {
      const mis_a_jour = await api.requete(`/api/v1/auth/utilisateurs/${id}/desactiver`, { methode: "POST" });
      const i = this.liste.findIndex((u) => u.id === id);
      if (i !== -1) this.liste[i] = mis_a_jour;
      return mis_a_jour;
    },

    async activer(id) {
      const mis_a_jour = await api.requete(`/api/v1/auth/utilisateurs/${id}/activer`, { methode: "POST" });
      const i = this.liste.findIndex((u) => u.id === id);
      if (i !== -1) this.liste[i] = mis_a_jour;
      return mis_a_jour;
    },
  },
});

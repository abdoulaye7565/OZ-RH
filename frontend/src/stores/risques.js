import { defineStore } from "pinia";
import api from "../services/api";

export const useRisquesStore = defineStore("risques", {
  state: () => ({
    liste: [],
    matrice: [],
    chargement: false,
    erreur: null,
  }),

  actions: {
    async charger() {
      this.chargement = true;
      this.erreur = null;
      try {
        const [liste, matrice] = await Promise.all([
          api.requete("/api/v1/risques"),
          api.requete("/api/v1/risques/matrice"),
        ]);
        this.liste = liste;
        this.matrice = matrice;
      } catch (e) {
        this.erreur = e instanceof api.ErreurApi ? e.message : "Impossible de charger le registre des risques";
      } finally {
        this.chargement = false;
      }
    },

    async creer(donnees) {
      const risque = await api.requete("/api/v1/risques", { methode: "POST", corps: donnees });
      this.liste.unshift(risque);
      return risque;
    },

    async reevaluer(risqueId, cotation) {
      await api.requete(`/api/v1/risques/${risqueId}/reevaluer`, { methode: "POST", corps: cotation });
      await this.charger();
    },

    // Corrige les champs descriptifs (danger, catégorie, unité, personnes
    // exposées) — pas la cotation, qui passe par reevaluer(). 2026-09-10.
    async modifier(risqueId, donnees) {
      await api.requete(`/api/v1/risques/${risqueId}`, { methode: "PATCH", corps: donnees });
      await this.charger();
    },
  },
});

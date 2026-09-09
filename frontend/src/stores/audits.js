import { defineStore } from "pinia";
import api from "../services/api";

export const useAuditsStore = defineStore("audits", {
  state: () => ({
    exigences: [],
    campagne: null,
    revues: [],
    utilisateurs: [],
    chargement: false,
    erreur: null,
  }),

  actions: {
    async charger() {
      this.chargement = true;
      this.erreur = null;
      try {
        const [exigences, utilisateurs] = await Promise.all([
          api.requete("/api/v1/audits/exigences"),
          api.requete("/api/v1/auth/utilisateurs"),
        ]);
        this.exigences = exigences;
        this.utilisateurs = utilisateurs;
      } catch (e) {
        this.erreur = e instanceof api.ErreurApi ? e.message : "Impossible de charger les audits";
      } finally {
        this.chargement = false;
      }
    },

    async ouvrirCampagne() {
      this.campagne = await api.requete("/api/v1/audits/campagnes", { methode: "POST", corps: {} });
    },

    async chargerCampagne(id) {
      this.campagne = await api.requete(`/api/v1/audits/campagnes/${id}`);
    },

    async coter(exigenceId, cotation, ecart) {
      await api.requete(`/api/v1/audits/campagnes/${this.campagne.id}/cotations`, {
        methode: "PATCH",
        corps: [{ exigence_id: exigenceId, cotation, ecart: ecart || null }],
      });
      await this.chargerCampagne(this.campagne.id);
    },

    async cloturerCampagne() {
      await api.requete(`/api/v1/audits/campagnes/${this.campagne.id}/cloturer`, { methode: "POST" });
      await this.chargerCampagne(this.campagne.id);
    },

    async creerRevue(donnees) {
      const revue = await api.requete("/api/v1/revues", { methode: "POST", corps: donnees });
      this.revues.unshift(revue);
      return revue;
    },

    async ajouterDecision(revueId, donnees) {
      await api.requete(`/api/v1/revues/${revueId}/decisions`, { methode: "POST", corps: donnees });
    },
  },
});

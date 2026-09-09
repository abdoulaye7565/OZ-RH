import { defineStore } from "pinia";
import api from "../services/api";

export const useActionsStore = defineStore("actions", {
  state: () => ({
    liste: [],
    synthese: null,
    utilisateurs: [],
    risques: [],
    chargement: false,
    erreur: null,
  }),

  getters: {
    nomUtilisateur: (state) => (id) => {
      const u = state.utilisateurs.find((u) => u.id === id);
      return u ? `${u.prenom} ${u.nom}` : null;
    },
  },

  actions: {
    async charger() {
      this.chargement = true;
      this.erreur = null;
      try {
        const [liste, synthese, utilisateurs, risques] = await Promise.all([
          api.requete("/api/v1/actions"),
          api.requete("/api/v1/actions/synthese"),
          api.requete("/api/v1/auth/utilisateurs"),
          api.requete("/api/v1/risques"),
        ]);
        this.liste = liste;
        this.synthese = synthese;
        this.utilisateurs = utilisateurs;
        this.risques = risques;
      } catch (e) {
        this.erreur = e instanceof api.ErreurApi ? e.message : "Impossible de charger le plan d'action";
      } finally {
        this.chargement = false;
      }
    },

    async creer(donnees) {
      const action = await api.requete("/api/v1/actions", { methode: "POST", corps: donnees });
      this.liste.unshift(action);
      return action;
    },

    async mettreAJourAvancement(actionId, avancement, indicateur) {
      const mis_a_jour = await api.requete(`/api/v1/actions/${actionId}/avancement`, {
        methode: "PATCH",
        corps: { avancement, indicateur },
      });
      const index = this.liste.findIndex((a) => a.id === actionId);
      if (index !== -1) this.liste[index] = mis_a_jour;
    },

    async changerStatut(actionId, statut) {
      const mis_a_jour = await api.requete(`/api/v1/actions/${actionId}/statut`, { methode: "PATCH", corps: { statut } });
      const index = this.liste.findIndex((a) => a.id === actionId);
      if (index !== -1) this.liste[index] = mis_a_jour;
    },
  },
});

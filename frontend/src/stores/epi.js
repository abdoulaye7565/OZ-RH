import { defineStore } from "pinia";
import api from "../services/api";

export const useEpiStore = defineStore("epi", {
  state: () => ({
    liste: [],
    utilisateurs: [],
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
        const [epi, utilisateurs] = await Promise.all([
          api.requete("/api/v1/epi"),
          api.requete("/api/v1/auth/utilisateurs"),
        ]);
        this.liste = epi;
        this.utilisateurs = utilisateurs;
      } catch (e) {
        this.erreur = e instanceof api.ErreurApi ? e.message : "Impossible de charger les EPI";
      } finally {
        this.chargement = false;
      }
    },

    async enregistrerVerification(epiId, conforme) {
      try {
        const mis_a_jour = await api.requete(`/api/v1/epi/${epiId}/verification-periodique`, {
          methode: "POST",
          corps: { conforme },
        });
        const index = this.liste.findIndex((e) => e.id === epiId);
        if (index !== -1) this.liste[index] = mis_a_jour;
      } catch (e) {
        this.erreur = e instanceof api.ErreurApi ? e.message : "Impossible d'enregistrer la vérification";
      }
    },
  },
});

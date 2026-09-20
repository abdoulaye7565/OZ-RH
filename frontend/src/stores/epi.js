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

    // Contrôle léger avant usage, par le porteur lui-même (2026-09-19, "tu
    // corriges tout") : POST /epi/{id}/verification-avant-utilisation existait
    // côté serveur depuis le prompt 2.1, ouvert à tout utilisateur
    // authentifié (contrairement à verification-periodique, réservée à
    // GERER_EPI) — jamais câblé, la maquette ne distinguant pas les deux
    // gestes à l'écran.
    async verifierAvantUtilisation(epiId, conforme) {
      const mis_a_jour = await api.requete(`/api/v1/epi/${epiId}/verification-avant-utilisation`, {
        methode: "POST",
        corps: { conforme },
      });
      const index = this.liste.findIndex((e) => e.id === epiId);
      if (index !== -1) this.liste[index] = mis_a_jour;
      return mis_a_jour;
    },

    // Registre EPI (2026-09-19, même campagne) : création, affectation,
    // retrait et réforme existaient tous côté serveur (prompt 2.1) sans
    // aucune UI, l'écran desktop n'étant qu'un tableau de lecture.
    async creer(donnees) {
      const cree = await api.requete("/api/v1/epi", { methode: "POST", corps: donnees });
      this.liste.push(cree);
      return cree;
    },

    async affecter(epiId, porteur_id) {
      const mis_a_jour = await api.requete(`/api/v1/epi/${epiId}/affectation`, {
        methode: "PATCH",
        corps: { porteur_id },
      });
      const index = this.liste.findIndex((e) => e.id === epiId);
      if (index !== -1) this.liste[index] = mis_a_jour;
      return mis_a_jour;
    },

    async retirer(epiId) {
      const mis_a_jour = await api.requete(`/api/v1/epi/${epiId}/retirer`, { methode: "POST" });
      const index = this.liste.findIndex((e) => e.id === epiId);
      if (index !== -1) this.liste[index] = mis_a_jour;
      return mis_a_jour;
    },

    async reformer(epiId, motif) {
      const mis_a_jour = await api.requete(`/api/v1/epi/${epiId}/reformer`, {
        methode: "POST",
        corps: { motif },
      });
      const index = this.liste.findIndex((e) => e.id === epiId);
      if (index !== -1) this.liste[index] = mis_a_jour;
      return mis_a_jour;
    },
  },
});

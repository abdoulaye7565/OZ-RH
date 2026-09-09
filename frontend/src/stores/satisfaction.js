import { defineStore } from "pinia";
import api from "../services/api";

export const useSatisfactionStore = defineStore("satisfaction", {
  state: () => ({
    enquetes: [],
    aTraiter: [],
    reponses: [],
    sites: [],
    utilisateurs: [],
    chargement: false,
    erreur: null,
  }),

  getters: {
    nomSite: (state) => (id) => state.sites.find((s) => s.id === id)?.nom ?? null,
    nomUtilisateur: (state) => (id) => {
      const u = state.utilisateurs.find((u) => u.id === id);
      return u ? `${u.prenom} ${u.nom}` : null;
    },
    // Moyenne par critère, calculée côté client à partir de toutes les
    // réponses reçues (aucune route ne renvoie cette agrégation déjà faite).
    moyenneParCritere: (state) => {
      const totaux = {};
      for (const r of state.reponses) {
        for (const n of r.notes) {
          if (!totaux[n.critere]) totaux[n.critere] = { somme: 0, n: 0 };
          totaux[n.critere].somme += n.note;
          totaux[n.critere].n += 1;
        }
      }
      const moyennes = {};
      for (const [critere, { somme, n }] of Object.entries(totaux)) moyennes[critere] = somme / n;
      return moyennes;
    },
    // Fonction normale (pas fléchée) : Pinia ne passe pas les autres getters en
    // second argument (contrairement à Vuex) — un autre getter s'obtient via
    // `this`, ce qui exige `this` correctement lié, donc pas de fonction fléchée.
    moyenneGlobale() {
      const valeurs = Object.values(this.moyenneParCritere);
      if (!valeurs.length) return null;
      return valeurs.reduce((a, b) => a + b, 0) / valeurs.length;
    },
    reponseParEnquete: (state) => (enqueteId) => state.reponses.find((r) => r.enquete_id === enqueteId) ?? null,
  },

  actions: {
    async charger() {
      this.chargement = true;
      this.erreur = null;
      try {
        const [enquetes, aTraiter, reponses, sites, utilisateurs] = await Promise.all([
          api.requete("/api/v1/satisfaction/enquetes"),
          api.requete("/api/v1/satisfaction/a-traiter"),
          api.requete("/api/v1/satisfaction/reponses"),
          api.requete("/api/v1/sites"),
          api.requete("/api/v1/auth/utilisateurs"),
        ]);
        this.enquetes = enquetes;
        this.aTraiter = aTraiter;
        this.reponses = reponses;
        this.sites = sites;
        this.utilisateurs = utilisateurs;
      } catch (e) {
        this.erreur = e instanceof api.ErreurApi ? e.message : "Impossible de charger la satisfaction client";
      } finally {
        this.chargement = false;
      }
    },

    async creerEnquete(donnees) {
      const enquete = await api.requete("/api/v1/satisfaction/enquetes", { methode: "POST", corps: donnees });
      this.enquetes.unshift(enquete);
      return enquete;
    },

    // --- Questionnaire public (sans authentification, accès par jeton) ---
    async chargerQuestionnaire(jeton) {
      return api.requete(`/api/v1/satisfaction/questionnaire/${jeton}`);
    },

    async repondre(jeton, donnees) {
      return api.requete(`/api/v1/satisfaction/questionnaire/${jeton}`, { methode: "POST", corps: donnees });
    },
  },
});

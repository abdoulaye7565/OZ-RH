import { defineStore } from "pinia";
import api from "../services/api";

export const useFormationsStore = defineStore("formations", {
  state: () => ({
    seances: [],
    mesHabilitations: [],
    competences: [],
    utilisateurs: [],
    questions: [],
    chargement: false,
    erreur: null,
  }),

  getters: {
    nomCompetence: (state) => (id) => state.competences.find((c) => c.id === id)?.libelle ?? null,
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
        const [seances, mesHabilitations, competences, utilisateurs] = await Promise.all([
          api.requete("/api/v1/formations/seances"),
          api.requete("/api/v1/formations/mes-habilitations"),
          api.requete("/api/v1/formations/competences"),
          api.requete("/api/v1/auth/utilisateurs"),
        ]);
        this.seances = seances;
        this.mesHabilitations = mesHabilitations;
        this.competences = competences;
        this.utilisateurs = utilisateurs;
      } catch (e) {
        this.erreur = e instanceof api.ErreurApi ? e.message : "Impossible de charger les formations";
      } finally {
        this.chargement = false;
      }
    },

    async creerCompetence(donnees) {
      const c = await api.requete("/api/v1/formations/competences", { methode: "POST", corps: donnees });
      this.competences.unshift(c);
      return c;
    },

    async creerSeance(donnees) {
      const s = await api.requete("/api/v1/formations/seances", { methode: "POST", corps: donnees });
      this.seances.unshift(s);
      return s;
    },

    // Corrige une séance encore planifiée (revue d'ensemble 2026-09-10) —
    // refusé serveur si déjà réalisée (409).
    async modifierSeance(seanceId, donnees) {
      const s = await api.requete(`/api/v1/formations/seances/${seanceId}`, { methode: "PATCH", corps: donnees });
      const i = this.seances.findIndex((x) => x.id === seanceId);
      if (i !== -1) this.seances[i] = s;
      return s;
    },

    async emarger(seanceId, participantId, present = true) {
      await api.requete(`/api/v1/formations/seances/${seanceId}/emargement`, {
        methode: "POST",
        corps: { participant_id: participantId, present },
      });
    },

    // Écran d'émargement + clôture de séance (2026-09-19, "tu corriges
    // tout") : `emarger()` ci-dessus existait déjà sans jamais être appelé
    // depuis un écran ; POST .../cloturer n'avait même pas d'action dédiée.
    // `listerEmargements` s'appuie sur la route de lecture ajoutée le même
    // jour côté serveur (GET .../emargements), sans laquelle un écran
    // rouvert ne saurait pas qui a déjà signé.
    async listerEmargements(seanceId) {
      return api.requete(`/api/v1/formations/seances/${seanceId}/emargements`);
    },

    async cloturerSeance(seanceId) {
      const s = await api.requete(`/api/v1/formations/seances/${seanceId}/cloturer`, { methode: "POST" });
      const i = this.seances.findIndex((x) => x.id === seanceId);
      if (i !== -1) this.seances[i] = s;
      return s;
    },

    async chargerQuestions() {
      this.questions = await api.requete("/api/v1/formations/questions-quiz");
    },

    async passerQuiz(seanceId, reponses) {
      return api.requete(`/api/v1/formations/seances/${seanceId}/quiz`, {
        methode: "POST",
        corps: { seance_id: seanceId, reponses },
      });
    },
  },
});

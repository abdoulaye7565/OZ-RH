import { defineStore } from "pinia";
import api from "../services/api";

export const usePermisStore = defineStore("permis", {
  state: () => ({
    liste: [],
    evaluationsSlam: [],
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
    permisActifs: (state) => state.liste.filter((p) => p.statut === "delivre"),
    enAttente: (state) => state.liste.filter((p) => p.statut === "demande" || p.statut === "bloque"),
  },

  actions: {
    // Chargement complet (écrans de pilotage — desktop et liste mobile) :
    // les évaluations SLAM et la liste des utilisateurs exigent des rôles de
    // pilotage (CONSULTER_TABLEAU_BORD) — un simple technicien peut charger
    // les permis mais pas le reste ; échoue proprement sur le compte du
    // technicien plutôt que de masquer l'erreur (voir `chargerPourDemande`
    // pour le sous-ensemble ouvert à tous).
    async charger() {
      this.chargement = true;
      this.erreur = null;
      try {
        const [liste, evaluationsSlam, sites, utilisateurs] = await Promise.all([
          api.requete("/api/v1/permis"),
          api.requete("/api/v1/slam"),
          api.requete("/api/v1/sites"),
          api.requete("/api/v1/auth/utilisateurs"),
        ]);
        this.liste = liste;
        this.evaluationsSlam = evaluationsSlam;
        this.sites = sites;
        this.utilisateurs = utilisateurs;
      } catch (e) {
        this.erreur = e instanceof api.ErreurApi ? e.message : "Impossible de charger les permis";
      } finally {
        this.chargement = false;
      }
    },

    // Sous-ensemble ouvert à tout utilisateur authentifié (technicien compris)
    // : sert à l'écran mobile "SLAM & permis", où /slam (liste complète) et
    // /auth/utilisateurs restent nécessaires, mais /slam est remplacée par
    // /slam/mes-evaluations (accessible à tous, contrairement à /slam).
    async chargerPourDemande() {
      this.chargement = true;
      this.erreur = null;
      try {
        const [liste, mesEvaluationsSlam, sites, utilisateurs] = await Promise.all([
          api.requete("/api/v1/permis"),
          api.requete("/api/v1/slam/mes-evaluations"),
          api.requete("/api/v1/sites"),
          api.requete("/api/v1/auth/utilisateurs"),
        ]);
        this.liste = liste;
        this.evaluationsSlam = mesEvaluationsSlam;
        this.sites = sites;
        this.utilisateurs = utilisateurs;
      } catch (e) {
        this.erreur = e instanceof api.ErreurApi ? e.message : "Impossible de charger les permis";
      } finally {
        this.chargement = false;
      }
    },

    async creer(donnees) {
      const permis = await api.requete("/api/v1/permis", { methode: "POST", corps: donnees });
      this.liste.unshift(permis);
      return permis;
    },
  },
});

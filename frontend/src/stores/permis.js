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

    // Écran de validation (responsable) : on n'a besoin que d'UN permis, mais
    // aussi des sites et des utilisateurs pour afficher des noms plutôt que
    // « Site #1 » / « Utilisateur #3 » — décisif ici, c'est l'écran qui
    // autorise un travail en hauteur (voir docs/JOURNAL.md 2026-09-10).
    async chargerPourValidation(id) {
      this.chargement = true;
      this.erreur = null;
      try {
        const [permis, sites, utilisateurs] = await Promise.all([
          api.requete(`/api/v1/permis/${id}`),
          this.sites.length ? Promise.resolve(this.sites) : api.requete("/api/v1/sites"),
          this.utilisateurs.length ? Promise.resolve(this.utilisateurs) : api.requete("/api/v1/auth/utilisateurs"),
        ]);
        this.sites = sites;
        this.utilisateurs = utilisateurs;
        const i = this.liste.findIndex((p) => p.id === permis.id);
        if (i !== -1) this.liste[i] = permis;
        else this.liste.push(permis);
        return permis;
      } catch (e) {
        this.erreur = e instanceof api.ErreurApi ? e.message : "Impossible de charger le permis";
        throw e;
      } finally {
        this.chargement = false;
      }
    },

    async valider(id) {
      const permis = await api.requete(`/api/v1/permis/${id}/valider`, { methode: "POST" });
      const i = this.liste.findIndex((p) => p.id === id);
      if (i !== -1) this.liste[i] = permis;
      return permis;
    },

    async refuser(id, motif) {
      const permis = await api.requete(`/api/v1/permis/${id}/refuser`, { methode: "POST", corps: { motif } });
      const i = this.liste.findIndex((p) => p.id === id);
      if (i !== -1) this.liste[i] = permis;
      return permis;
    },

    // POST .../cloturer existait côté serveur (testé) sans aucune UI
    // (2026-09-19, "tu corriges tout") : un permis délivré restait
    // éternellement "en cours", jamais marqué clôturé une fois les travaux
    // terminés.
    async cloturer(id) {
      const permis = await api.requete(`/api/v1/permis/${id}/cloturer`, { methode: "POST" });
      const i = this.liste.findIndex((p) => p.id === id);
      if (i !== -1) this.liste[i] = permis;
      return permis;
    },
  },
});

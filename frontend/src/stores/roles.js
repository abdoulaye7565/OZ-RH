import { defineStore } from "pinia";
import api from "../services/api";

// Source unique des permissions réelles (revue d'ensemble 2026-09-10 —
// GET /api/v1/roles, lu par introspection de app/core/permissions.py côté
// serveur). Utilisée à la fois par la grille "Permissions par rôle"
// (UtilisateursDesktopView) et par la visibilité des liens de la barre
// latérale (GestionLayout) — pour que les deux ne puissent plus jamais
// diverger l'une de l'autre, ni de ce que les routes appliquent réellement.
//
// Contexte du bug corrigé : la barre latérale montrait "Tableau de bord",
// "SLAM & permis", "Formations" et "Satisfaction" à TOUS les rôles, alors
// que leurs données (competences, /slam, /satisfaction/enquetes...) sont
// réservées aux rôles de pilotage côté serveur — un technicien ou un
// collaborateur qui cliquait dessus tombait sur un écran vide/en erreur
// (403). Le menu mobile (MenuView.vue, `peutVoirTableauBord`) avait déjà la
// bonne restriction ; la barre latérale desktop ne l'avait jamais reçue.
export const useRolesStore = defineStore("roles", {
  state: () => ({
    donnees: null, // { roles: [...], permissions: [...] } | null tant que non chargé
    chargement: false,
    erreur: null,
  }),

  getters: {
    // Rôles autorisés pour une clé de permission (ex. "CONSULTER_TABLEAU_BORD"),
    // ou null si la clé est inconnue de l'API (permission jamais déclarée
    // côté serveur — traité par l'appelant comme "pas de restriction connue",
    // jamais comme "fermé à tous", pour ne pas cacher un module par erreur
    // de frappe sur une clé).
    rolesPour: (state) => (cle) => state.donnees?.permissions.find((p) => p.cle === cle)?.roles ?? null,
  },

  actions: {
    async charger() {
      // Une seule fois par session : les permissions sont du code, elles ne
      // changent jamais en cours de session (pas de re-fetch à chaque
      // navigation entre écrans de gestion).
      if (this.donnees || this.chargement) return;
      this.chargement = true;
      this.erreur = null;
      try {
        this.donnees = await api.requete("/api/v1/roles");
      } catch (e) {
        this.erreur = e instanceof api.ErreurApi ? e.message : "Impossible de charger les rôles";
      } finally {
        this.chargement = false;
      }
    },
  },
});

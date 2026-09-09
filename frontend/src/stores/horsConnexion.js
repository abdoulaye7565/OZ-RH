/**
 * Orchestration de la synchronisation hors connexion (voir services/filesync.js
 * pour le mécanisme de stockage). Ce store ne connaît aucun module métier par
 * lui-même — chaque module s'enregistre via enregistrerGestionnaire(), câblé
 * une seule fois au démarrage (main.js) pour éviter tout import circulaire
 * entre stores.
 */
import { defineStore } from "pinia";
import filesync from "../services/filesync";

export const useHorsConnexionStore = defineStore("horsConnexion", {
  state: () => ({
    gestionnaires: {},
    compteEnAttente: 0,
    synchronisationEnCours: false,
    derniereSynchronisation: null,
  }),

  actions: {
    enregistrerGestionnaire(type, { executer, onSucces }) {
      this.gestionnaires[type] = { executer, onSucces };
    },

    async rafraichirCompte() {
      try {
        this.compteEnAttente = await filesync.compterEnAttente();
      } catch {
        // IndexedDB indisponible (navigation privée stricte, quotas) : le
        // compteur reste simplement à sa dernière valeur connue.
      }
    },

    async ajouterEnAttente(type, champs, fichiers) {
      const element = await filesync.ajouterEnAttente(type, champs, fichiers);
      await this.rafraichirCompte();
      return element;
    },

    async synchroniser() {
      if (this.synchronisationEnCours || !navigator.onLine) return;
      this.synchronisationEnCours = true;
      try {
        await filesync.synchroniser(this.gestionnaires);
        this.derniereSynchronisation = new Date().toISOString();
      } finally {
        this.synchronisationEnCours = false;
        await this.rafraichirCompte();
      }
    },

    demarrerEcouteReseau() {
      window.addEventListener("online", () => this.synchroniser());
    },
  },
});

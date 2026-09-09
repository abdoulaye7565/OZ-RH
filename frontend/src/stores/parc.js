import { defineStore } from "pinia";
import api from "../services/api";

export const useParcStore = defineStore("parc", {
  state: () => ({
    liste: [],
    sites: [],
    fiche: null,
    chargement: false,
    chargementFiche: false,
    erreur: null,
  }),

  getters: {
    nomSite: (state) => (id) => state.sites.find((s) => s.id === id)?.nom ?? null,
  },

  actions: {
    async charger() {
      this.chargement = true;
      this.erreur = null;
      try {
        const [liste, sites] = await Promise.all([api.requete("/api/v1/equipements"), api.requete("/api/v1/sites")]);
        this.liste = liste;
        this.sites = sites;
      } catch (e) {
        this.erreur = e instanceof api.ErreurApi ? e.message : "Impossible de charger le parc d'équipements";
      } finally {
        this.chargement = false;
      }
    },

    async chargerFiche(equipementId) {
      this.chargementFiche = true;
      this.erreur = null;
      try {
        this.fiche = await api.requete(`/api/v1/equipements/${equipementId}/fiche`);
      } catch (e) {
        this.erreur = e instanceof api.ErreurApi ? e.message : "Impossible de charger la fiche équipement";
      } finally {
        this.chargementFiche = false;
      }
    },

    async creerEquipement(donnees) {
      const equipement = await api.requete("/api/v1/equipements", { methode: "POST", corps: donnees });
      this.liste.unshift(equipement);
      return equipement;
    },

    async creerConfiguration(equipementId, champs) {
      const donnees = new FormData();
      donnees.set("equipement_id", equipementId);
      for (const [cle, valeur] of Object.entries(champs)) {
        if (valeur !== null && valeur !== undefined && valeur !== "") donnees.set(cle, valeur);
      }
      await api.requete("/api/v1/configurations", { methode: "POST", corps: donnees });
      await this.chargerFiche(equipementId);
    },
  },
});

import { defineStore } from "pinia";
import api from "../services/api";

export const useTableauBordStore = defineStore("tableauBord", {
  state: () => ({
    donnees: null,
    chargement: false,
    erreur: null,
  }),

  actions: {
    async charger({ siteId, dateDebut, dateFin } = {}) {
      this.chargement = true;
      this.erreur = null;
      try {
        const parametres = new URLSearchParams();
        if (siteId) parametres.set("site_id", siteId);
        if (dateDebut) parametres.set("date_debut", dateDebut);
        if (dateFin) parametres.set("date_fin", dateFin);
        const suffixe = parametres.toString() ? `?${parametres}` : "";
        this.donnees = await api.requete(`/api/v1/tableau-de-bord${suffixe}`);
      } catch (e) {
        this.erreur = e instanceof api.ErreurApi ? e.message : "Impossible de charger le tableau de bord";
      } finally {
        this.chargement = false;
      }
    },
  },
});

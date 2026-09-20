import { defineStore } from "pinia";
import api from "../services/api";

export const useVisiteursStore = defineStore("visiteurs", {
  state: () => ({
    presents: [],
    liste: [],
    chargement: false,
    erreur: null,
  }),

  actions: {
    async charger() {
      this.chargement = true;
      this.erreur = null;
      try {
        const [presents, liste] = await Promise.all([
          api.requete("/api/v1/visiteurs/presents"),
          api.requete("/api/v1/visiteurs"),
        ]);
        this.presents = presents;
        this.liste = liste;
      } catch (e) {
        this.erreur = e instanceof api.ErreurApi ? e.message : "Impossible de charger les visiteurs";
      } finally {
        this.chargement = false;
      }
    },

    async enregistrer(donnees) {
      await api.requete("/api/v1/visiteurs", { methode: "POST", corps: donnees });
      await this.charger();
    },

    async enregistrerDepart(id) {
      await api.requete(`/api/v1/visiteurs/${id}/depart`, { methode: "POST" });
      await this.charger();
    },

    // Réservé à un visiteur déjà parti (le serveur le revérifie de toute
    // façon, point 9 CLAUDE.md) — voir docs/JOURNAL.md, 2026-09-09.
    async archiver(id) {
      await api.requete(`/api/v1/visiteurs/${id}/archiver`, { methode: "POST" });
      await this.charger();
    },
  },
});

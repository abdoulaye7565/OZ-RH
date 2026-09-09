import { defineStore } from "pinia";
import api from "../services/api";

export const useDocumentsStore = defineStore("documents", {
  state: () => ({
    liste: [],
    chargement: false,
    erreur: null,
  }),

  actions: {
    async charger() {
      this.chargement = true;
      this.erreur = null;
      try {
        this.liste = await api.requete("/api/v1/documents");
      } catch (e) {
        this.erreur = e instanceof api.ErreurApi ? e.message : "Impossible de charger les documents";
      } finally {
        this.chargement = false;
      }
    },

    async creer({ reference, intitule, niveau, confidentialite, fichier }) {
      const donnees = new FormData();
      donnees.set("reference", reference);
      donnees.set("intitule", intitule);
      donnees.set("niveau", niveau);
      donnees.set("confidentialite", confidentialite);
      if (fichier) donnees.set("fichier", fichier);
      const document = await api.requete("/api/v1/documents", { methode: "POST", corps: donnees });
      this.liste.unshift(document);
      return document;
    },

    async soumettreApprobation(id) {
      const d = await api.requete(`/api/v1/documents/${id}/soumettre-approbation`, { methode: "POST" });
      this._remplacer(d);
    },

    async approuver(id) {
      const d = await api.requete(`/api/v1/documents/${id}/approuver`, { methode: "POST" });
      this._remplacer(d);
    },

    async accuserLecture(id) {
      const d = await api.requete(`/api/v1/documents/${id}/accuser-lecture`, { methode: "POST" });
      this._remplacer(d);
    },

    _remplacer(document) {
      const index = this.liste.findIndex((d) => d.id === document.id);
      if (index !== -1) this.liste[index] = document;
    },
  },
});

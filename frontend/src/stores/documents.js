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

    // Corrige les métadonnées d'un brouillon (revue d'ensemble 2026-09-10) —
    // refusé serveur au-delà du brouillon (409).
    async modifier(id, donnees) {
      const d = await api.requete(`/api/v1/documents/${id}`, { methode: "PATCH", corps: donnees });
      this._remplacer(d);
      return d;
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

    // POST .../nouvelle-version existait côté serveur (testé) sans aucune UI
    // (2026-09-19, "tu corriges tout") : un document en vigueur ne pouvait
    // jamais être révisé — seule une correction de brouillon (modifier())
    // était possible. Crée une NOUVELLE fiche (nouvel id, repart en
    // brouillon), ne remplace pas l'ancienne dans la liste : les deux
    // versions restent consultables, comme l'exige l'immutabilité des
    // documents en vigueur (règle 5, CLAUDE.md).
    async nouvelleVersion(id, fichier) {
      const donnees = new FormData();
      if (fichier) donnees.set("fichier", fichier);
      const nouveau = await api.requete(`/api/v1/documents/${id}/nouvelle-version`, { methode: "POST", corps: donnees });
      this.liste.unshift(nouveau);
      return nouveau;
    },

    _remplacer(document) {
      const index = this.liste.findIndex((d) => d.id === document.id);
      if (index !== -1) this.liste[index] = document;
    },
  },
});

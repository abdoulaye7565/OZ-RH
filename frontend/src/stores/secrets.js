import { defineStore } from "pinia";
import api from "../services/api";

export const TYPES_ACCES = [
  { valeur: "administration", libelle: "Administration" },
  { valeur: "cle_reseau", libelle: "Clé réseau" },
  { valeur: "compte_cloud", libelle: "Compte cloud" },
  { valeur: "autre", libelle: "Autre" },
];

export const ROLES_SECRET = [
  { valeur: "technicien", libelle: "Technicien+", tag: "t-gy" },
  { valeur: "responsable", libelle: "Responsable+", tag: "t-or" },
  { valeur: "administrateur", libelle: "Direction", tag: "t-red" },
];

// Délai de masquage automatique d'un secret affiché — cohérent avec la
// maquette (#s-vault : "se masque après 15 secondes") et la valeur par
// défaut du backend (secret_service.DELAI_MASQUAGE_SECONDES).
export const DELAI_MASQUAGE_MS = 15000;

export const useSecretsStore = defineStore("secrets", {
  state: () => ({
    liste: [],
    equipements: [],
    utilisateurs: [],
    journal: {}, // secret_id -> entrées
    chargement: false,
    erreur: null,
  }),

  getters: {
    nomEquipement: (state) => (id) => state.equipements.find((e) => e.id === id)?.identity ?? null,
    nomUtilisateur: (state) => (id) => {
      const u = state.utilisateurs.find((u) => u.id === id);
      return u ? `${u.prenom} ${u.nom}` : null;
    },
    infoRole: () => (valeur) => ROLES_SECRET.find((r) => r.valeur === valeur) ?? { libelle: valeur, tag: "t-gy" },
  },

  actions: {
    async charger() {
      this.chargement = true;
      this.erreur = null;
      try {
        const [liste, equipements, utilisateurs] = await Promise.all([
          api.requete("/api/v1/secrets"),
          api.requete("/api/v1/equipements"),
          api.requete("/api/v1/auth/utilisateurs"),
        ]);
        this.liste = liste;
        this.equipements = equipements;
        this.utilisateurs = utilisateurs;
      } catch (e) {
        this.erreur = e instanceof api.ErreurApi ? e.message : "Impossible de charger le coffre-fort";
      } finally {
        this.chargement = false;
      }
    },

    async creer(donnees) {
      const secret = await api.requete("/api/v1/secrets", { methode: "POST", corps: donnees });
      this.liste.unshift(secret);
      return secret;
    },

    async modifier(id, donnees) {
      const secret = await api.requete(`/api/v1/secrets/${id}`, { methode: "PATCH", corps: donnees });
      const i = this.liste.findIndex((s) => s.id === id);
      if (i !== -1) this.liste[i] = secret;
      return secret;
    },

    async archiver(id) {
      await api.requete(`/api/v1/secrets/${id}/archiver`, { methode: "POST" });
      this.liste = this.liste.filter((s) => s.id !== id);
    },

    // Renvoie la valeur en clair — jamais mise en cache dans le store
    // au-delà de l'appel : chaque affichage doit rester une consultation
    // explicite, tracée côté serveur (règle 5.2.4).
    async consulter(id) {
      const reponse = await api.requete(`/api/v1/secrets/${id}/consulter`, { methode: "POST" });
      return reponse.valeur;
    },

    async chargerJournal(id) {
      this.journal[id] = await api.requete(`/api/v1/secrets/${id}/journal`);
      return this.journal[id];
    },

    async genererMotDePasse(longueur = 20, inclureSymboles = true) {
      const reponse = await api.requete("/api/v1/secrets/generer-mot-de-passe", {
        methode: "POST",
        corps: { longueur, inclure_symboles: inclureSymboles },
      });
      return reponse.mot_de_passe;
    },
  },
});

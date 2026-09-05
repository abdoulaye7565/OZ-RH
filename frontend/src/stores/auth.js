/**
 * Store d'authentification minimal.
 *
 * Aucun prompt du lotissement ne couvre explicitement un écran de connexion
 * avant celui-ci : sans lui, les écrans Signalements demandés au prompt 1.3 ne
 * peuvent tout simplement pas être exercés (l'API exige un jeton). Ajouté par
 * nécessité, volontairement minimal — pas de rafraîchissement automatique du
 * jeton ici, seulement la connexion et le stockage du jeton d'accès.
 */
import { defineStore } from "pinia";
import api from "../services/api";

export const useAuthStore = defineStore("auth", {
  state: () => ({
    jeton: api.lireJeton(),
    utilisateur: null,
    enCours: false,
    erreur: null,
  }),

  getters: {
    estConnecte: (etat) => Boolean(etat.jeton),
  },

  actions: {
    async connecter(identifiant, motDePasse) {
      this.enCours = true;
      this.erreur = null;
      try {
        const reponse = await api.requete("/api/v1/auth/connexion", {
          methode: "POST",
          corps: { identifiant, mot_de_passe: motDePasse },
        });
        this.jeton = reponse.access_token;
        api.ecrireJeton(reponse.access_token);
        this.utilisateur = await api.requete("/api/v1/auth/moi");
        return true;
      } catch (e) {
        this.erreur = e instanceof api.ErreurApi ? e.message : "Connexion impossible";
        return false;
      } finally {
        this.enCours = false;
      }
    },

    deconnecter() {
      this.jeton = null;
      this.utilisateur = null;
      api.ecrireJeton(null);
    },
  },
});

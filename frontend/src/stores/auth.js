/**
 * Store d'authentification.
 *
 * Aucun prompt du lotissement ne couvre explicitement un écran de connexion
 * avant celui-ci : sans lui, les écrans Signalements demandés au prompt 1.3 ne
 * peuvent tout simplement pas être exercés (l'API exige un jeton). Ajouté par
 * nécessité.
 *
 * Rafraîchissement automatique du jeton d'accès (2026-09-08) : l'access token
 * expire en 15 minutes (config.py) ; sans ça, toute session active plus de
 * 15 minutes tombait en erreur générique à la moindre requête, y compris — de
 * façon trompeuse — sur un signalement saisi hors connexion (stores/
 * horsConnexion.js), qu'un 401 n'a aucune raison de mettre en file : ce n'est
 * pas un problème réseau, une nouvelle tentative sans jeton valide donnerait
 * le même résultat. Le rafraîchissement lui-même vit dans services/api.js
 * (silencieux, retenté une seule fois par requête) ; ce store se contente de
 * stocker le refresh token à la connexion et de le nettoyer à la déconnexion.
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
        api.ecrireJetonRafraichissement(reponse.refresh_token);
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
      api.ecrireJetonRafraichissement(null);
    },

    async chargerProfil() {
      // Reconstitue `utilisateur` après un rechargement de page : seul `jeton`
      // survit (localStorage), voir le commentaire de state ci-dessus et
      // router/index.js. Un jeton devenu invalide (expiré, compte désactivé)
      // déconnecte proprement plutôt que de laisser un état incohérent
      // (estConnecte=true, utilisateur=null indéfiniment).
      try {
        this.utilisateur = await api.requete("/api/v1/auth/moi");
      } catch {
        this.deconnecter();
      }
    },
  },
});

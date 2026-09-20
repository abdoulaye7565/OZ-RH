/**
 * Store Pinia dédié au module Signalements (prompt 1.3).
 *
 * Ne fait que relayer l'API : la validation métier (transitions de statut,
 * anonymat, référence SIG-AAAA-NNN…) reste entièrement côté serveur, ce store
 * ne fait aucune hypothèse dessus.
 *
 * Module pilote du mode hors connexion (2026-09-08, voir stores/horsConnexion.js
 * et services/filesync.js) : c'est le cas d'usage le plus critique du CDC
 * (technicien sur un pylône, zéro réseau) et l'écran qui annonçait déjà cette
 * limite. Une erreur réseau (pas un refus serveur) sur creer() met l'élément
 * en file au lieu de faire échouer la saisie.
 */
import { defineStore } from "pinia";
import api from "../services/api";
import { useHorsConnexionStore } from "./horsConnexion";
import { useAuthStore } from "./auth";

export const FILTRES_STATUT = [
  { valeur: null, libelle: "Tous" },
  { valeur: "nouveau", libelle: "Nouveaux" },
  { valeur: "en_analyse", libelle: "En analyse" },
  { valeur: "actions_definies", libelle: "Actions définies" },
  { valeur: "cloture", libelle: "Clôturés" },
];

// Filtre par type ajouté le 2026-09-08 (retour direct de l'utilisateur, "je
// ne vois pas l'écran des accidents") : GET /signalements acceptait déjà
// `type` côté API (prompt 1.3), jamais exploité côté écran jusqu'ici.
export const FILTRES_TYPE = [
  { valeur: null, libelle: "Tous les types" },
  { valeur: "situation_dangereuse", libelle: "Situation dangereuse" },
  { valeur: "presque_accident", libelle: "Presque-accident" },
  { valeur: "anomalie", libelle: "Anomalie" },
  { valeur: "incident", libelle: "Incident" },
  { valeur: "accident", libelle: "Accident" },
];

export const useSignalementsStore = defineStore("signalements", {
  state: () => ({
    liste: [],
    filtreStatut: null,
    filtreType: null,
    chargement: false,
    erreur: null,
    envoiEnCours: false,
  }),

  getters: {
    listeFiltree: (etat) => etat.liste,
    nombreParStatut: (etat) => {
      const compte = { nouveau: 0, en_analyse: 0, actions_definies: 0, cloture: 0 };
      for (const s of etat.liste) {
        // Un élément en attente de réseau n'a pas encore de statut serveur
        // réel : il ne compte dans aucun des onglets de statut.
        if (!s.enAttente && s.statut in compte) compte[s.statut] += 1;
      }
      return compte;
    },
  },

  actions: {
    async charger() {
      this.chargement = true;
      this.erreur = null;
      try {
        const parametres = new URLSearchParams();
        if (this.filtreStatut) parametres.set("statut", this.filtreStatut);
        if (this.filtreType) parametres.set("type", this.filtreType);
        const suffixe = parametres.toString() ? `?${parametres}` : "";
        this.liste = await api.requete(`/api/v1/signalements${suffixe}`);
      } catch (e) {
        this.erreur = e instanceof api.ErreurApi ? e.message : "Impossible de charger les signalements";
      } finally {
        this.chargement = false;
      }
    },

    // Fiche détail (2026-09-19, même campagne) : chargement individuel, à
    // ne pas confondre avec `liste` qui ne sert qu'à l'écran de liste — la
    // fiche détail doit refléter l'état serveur exact après chaque action.
    async obtenir(id) {
      return api.requete(`/api/v1/signalements/${id}`);
    },

    // Workflow de traitement (2026-09-19, retour direct de l'utilisateur —
    // "tu corriges tout" suite à l'audit de compatibilité front/back) :
    // PATCH /signalements/{id}/statut existait côté serveur (avec ses
    // transitions vérifiées, voir TRANSITIONS_AUTORISEES) depuis le tout
    // premier prompt, jamais câblé à un bouton. Réservé aux rôles habilités
    // (TRAITER_SIGNALEMENTS) — un rôle non habilité qui tenterait quand même
    // se voit renvoyer le message serveur tel quel.
    async changerStatut(id, statut) {
      const mis_a_jour = await api.requete(`/api/v1/signalements/${id}/statut`, {
        methode: "PATCH",
        corps: { statut },
      });
      const i = this.liste.findIndex((s) => s.id === id);
      if (i !== -1) this.liste[i] = mis_a_jour;
      return mis_a_jour;
    },

    async archiver(id) {
      await api.requete(`/api/v1/signalements/${id}/archiver`, { methode: "POST" });
      await this.charger();
    },

    definirFiltre(statut) {
      this.filtreStatut = statut;
      return this.charger();
    },

    definirFiltreType(type) {
      this.filtreType = type;
      return this.charger();
    },

    /**
     * Envoi réel vers l'API — extrait de creer() pour être rejouable tel quel
     * par la file d'attente hors connexion (stores/horsConnexion.js) une fois
     * le réseau revenu, sans dupliquer la construction du FormData.
     * @param {object} champs - type, site_id, lieu, description, anonyme, date_constat
     * @param {File[]} photos
     */
    async envoyerVersServeur(champs, photos) {
      const formulaire = new FormData();
      for (const [cle, valeur] of Object.entries(champs)) {
        formulaire.append(cle, valeur);
      }
      for (const photo of photos ?? []) {
        formulaire.append("photos", photo);
      }
      return api.requete("/api/v1/signalements", { methode: "POST", corps: formulaire });
    },

    /**
     * @param {object} champs - type, site_id, lieu, description, anonyme, date_constat
     * @param {File[]} photos
     */
    async creer(champs, photos) {
      this.envoiEnCours = true;
      this.erreur = null;
      try {
        const signalement = await this.envoyerVersServeur(champs, photos);
        this.liste.unshift(signalement);
        return signalement;
      } catch (e) {
        // Une erreur réseau (fetch n'a même pas pu joindre le serveur) signifie
        // qu'on est hors connexion : on met en file au lieu de faire échouer la
        // saisie (CLAUDE.md, contrainte fondatrice n°1). Un vrai refus serveur
        // (422 de validation, 401…) remonte, lui, normalement à l'écran — ce
        // n'est pas un problème réseau, une nouvelle tentative donnerait le
        // même résultat.
        if (e instanceof TypeError) {
          const horsConnexion = useHorsConnexionStore();
          const element = await horsConnexion.ajouterEnAttente("signalement", champs, photos);
          const auth = useAuthStore();
          const local = {
            id: `local-${element.id}`,
            reference: null,
            statut: "nouveau",
            enAttente: true,
            ...champs,
            photos: [],
            date_saisie: element.dateCreation,
            auteur_id: champs.anonyme ? null : auth.utilisateur?.id,
          };
          this.liste.unshift(local);
          return local;
        }
        this.erreur = e instanceof api.ErreurApi ? e.message : "Envoi impossible, réessayez";
        throw e;
      } finally {
        this.envoiEnCours = false;
      }
    },
  },
});

/**
 * Store Pinia dédié au module Signalements (prompt 1.3).
 *
 * Ne fait que relayer l'API : la validation métier (transitions de statut,
 * anonymat, référence SIG-AAAA-NNN…) reste entièrement côté serveur, ce store
 * ne fait aucune hypothèse dessus.
 */
import { defineStore } from "pinia";
import api from "../services/api";

export const FILTRES_STATUT = [
  { valeur: null, libelle: "Tous" },
  { valeur: "nouveau", libelle: "Nouveaux" },
  { valeur: "en_analyse", libelle: "En analyse" },
  { valeur: "actions_definies", libelle: "Actions définies" },
  { valeur: "cloture", libelle: "Clôturés" },
];

export const useSignalementsStore = defineStore("signalements", {
  state: () => ({
    liste: [],
    filtreStatut: null,
    chargement: false,
    erreur: null,
    envoiEnCours: false,
  }),

  getters: {
    listeFiltree: (etat) => etat.liste,
    nombreParStatut: (etat) => {
      const compte = { nouveau: 0, en_analyse: 0, actions_definies: 0, cloture: 0 };
      for (const s of etat.liste) {
        if (s.statut in compte) compte[s.statut] += 1;
      }
      return compte;
    },
  },

  actions: {
    async charger() {
      this.chargement = true;
      this.erreur = null;
      try {
        const chemin = this.filtreStatut
          ? `/api/v1/signalements?statut=${this.filtreStatut}`
          : "/api/v1/signalements";
        this.liste = await api.requete(chemin);
      } catch (e) {
        this.erreur = e instanceof api.ErreurApi ? e.message : "Impossible de charger les signalements";
      } finally {
        this.chargement = false;
      }
    },

    definirFiltre(statut) {
      this.filtreStatut = statut;
      return this.charger();
    },

    /**
     * @param {object} champs - type, site_id, lieu, description, anonyme, date_constat
     * @param {File[]} photos
     */
    async creer(champs, photos) {
      this.envoiEnCours = true;
      this.erreur = null;
      try {
        const formulaire = new FormData();
        for (const [cle, valeur] of Object.entries(champs)) {
          formulaire.append(cle, valeur);
        }
        for (const photo of photos) {
          formulaire.append("photos", photo);
        }
        const signalement = await api.requete("/api/v1/signalements", {
          methode: "POST",
          corps: formulaire,
        });
        this.liste.unshift(signalement);
        return signalement;
      } finally {
        this.envoiEnCours = false;
      }
      // Les erreurs de création (422 de validation serveur, 401…) sont laissées
      // remonter à l'appelant : l'écran de saisie doit pouvoir les afficher au
      // bon endroit du formulaire, pas seulement dans un message générique.
    },
  },
});

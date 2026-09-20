import { defineStore } from "pinia";
import api from "../services/api";

export const useAuditsStore = defineStore("audits", {
  state: () => ({
    exigences: [],
    campagne: null,
    revues: [],
    revueDetail: null,
    utilisateurs: [],
    chargement: false,
    erreur: null,
  }),

  actions: {
    async charger() {
      this.chargement = true;
      this.erreur = null;
      try {
        const [exigences, utilisateurs, revues] = await Promise.all([
          api.requete("/api/v1/audits/exigences"),
          api.requete("/api/v1/auth/utilisateurs"),
          // GET /revues existait depuis le 2026-09-19 seulement ("tu corriges
          // tout") : avant, aucune route ne permettait de retrouver les revues
          // déjà créées. Réservé à GERER_REVUES (referent_sheq/responsable/
          // administrateur) — un rôle sans ce droit reçoit un 403 ici, absorbé
          // en liste vide plutôt que de faire échouer tout `charger()`.
          api.requete("/api/v1/revues").catch(() => []),
        ]);
        this.exigences = exigences;
        this.utilisateurs = utilisateurs;
        this.revues = revues;
      } catch (e) {
        this.erreur = e instanceof api.ErreurApi ? e.message : "Impossible de charger les audits";
      } finally {
        this.chargement = false;
      }
    },

    async ouvrirCampagne() {
      this.campagne = await api.requete("/api/v1/audits/campagnes", { methode: "POST", corps: {} });
    },

    async chargerCampagne(id) {
      this.campagne = await api.requete(`/api/v1/audits/campagnes/${id}`);
    },

    async coter(exigenceId, cotation, ecart) {
      await api.requete(`/api/v1/audits/campagnes/${this.campagne.id}/cotations`, {
        methode: "PATCH",
        corps: [{ exigence_id: exigenceId, cotation, ecart: ecart || null }],
      });
      await this.chargerCampagne(this.campagne.id);
    },

    async cloturerCampagne() {
      await api.requete(`/api/v1/audits/campagnes/${this.campagne.id}/cloturer`, { methode: "POST" });
      await this.chargerCampagne(this.campagne.id);
    },

    async creerRevue(donnees) {
      const revue = await api.requete("/api/v1/revues", { methode: "POST", corps: donnees });
      this.revues.unshift(revue);
      return revue;
    },

    async ajouterDecision(revueId, donnees) {
      await api.requete(`/api/v1/revues/${revueId}/decisions`, { methode: "POST", corps: donnees });
    },

    // Fiche détail d'une revue déjà créée (2026-09-19, "tu corriges tout") :
    // commentaire IA (génération/édition/validation) et solde des décisions
    // existaient tous côté serveur (prompt 6.4 et 4.2) sans aucune UI.
    async chargerRevueDetail(id) {
      this.revueDetail = await api.requete(`/api/v1/revues/${id}`);
      return this.revueDetail;
    },

    // Object.assign sur l'objet existant plutôt que réaffecter `revueDetail`
    // à une toute nouvelle référence : bug réel trouvé en vérifiant en
    // conditions réelles ce lot-ci — la réaffectation laissait des boutons de
    // l'écran (état local du composant, sans lien avec revueDetail) figés
    // "disabled" après l'appel, alors que l'état réactif sous-jacent était
    // correct (confirmé en instrumentant le composant). Muter l'objet en
    // place évite la resynchronisation qui déclenchait ce blocage.
    async genererCommentaire(id) {
      const resultat = await api.requete(`/api/v1/revues/${id}/commentaire/generer`, { methode: "POST" });
      Object.assign(this.revueDetail, resultat);
      return this.revueDetail;
    },

    async modifierCommentaire(id, texte) {
      const resultat = await api.requete(`/api/v1/revues/${id}/commentaire`, { methode: "PATCH", corps: { texte } });
      Object.assign(this.revueDetail, resultat);
      return this.revueDetail;
    },

    async validerCommentaire(id) {
      const resultat = await api.requete(`/api/v1/revues/${id}/commentaire/valider`, { methode: "POST" });
      Object.assign(this.revueDetail, resultat);
      return this.revueDetail;
    },

    async solderDecision(decisionId) {
      const decision = await api.requete(`/api/v1/revues/decisions/${decisionId}/solder`, { methode: "POST" });
      if (this.revueDetail?.decisions) {
        const i = this.revueDetail.decisions.findIndex((d) => d.id === decisionId);
        if (i !== -1) this.revueDetail.decisions[i] = decision;
      }
      return decision;
    },
  },
});

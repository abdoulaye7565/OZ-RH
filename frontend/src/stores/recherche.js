import { defineStore } from "pinia";
import api from "../services/api";

// Recherche globale d'en-tête (revue d'ensemble 2026-09-10) : interroge
// `/api/v1/recherche` et mappe chaque type de résultat vers sa route.

// Un résultat → où cliquer atterrit. Les écrans de gestion desktop ont leur
// propre recherche interne : on ouvre l'écran, l'utilisateur affine ensuite.
const ROUTES_PAR_TYPE = {
  signalement: { name: "gestion-tableau-de-bord" }, // pas d'écran détail signalement desktop
  risque: { name: "gestion-risques" },
  action: { name: "gestion-actions" },
  permis: { name: "gestion-permis" },
  equipement: { name: "parc-fiche" }, // params.id ajouté ci-dessous
  document: { name: "gestion-documents" },
};

export function routeDeResultat(r) {
  const base = ROUTES_PAR_TYPE[r.type];
  if (!base) return null;
  if (r.type === "equipement") return { ...base, params: { id: r.id } };
  return base;
}

export const LIBELLE_TYPE = {
  signalement: "Signalement",
  risque: "Risque",
  action: "Action",
  permis: "Permis",
  equipement: "Équipement",
  document: "Document",
};

export const useRechercheStore = defineStore("recherche", {
  state: () => ({
    terme: "",
    resultats: [],
    chargement: false,
    ouvert: false,
  }),

  actions: {
    async lancer(terme) {
      this.terme = terme;
      if (terme.trim().length < 2) {
        this.resultats = [];
        this.ouvert = false;
        return;
      }
      this.chargement = true;
      try {
        this.resultats = await api.requete(`/api/v1/recherche?q=${encodeURIComponent(terme.trim())}`);
        this.ouvert = true;
      } catch {
        this.resultats = [];
      } finally {
        this.chargement = false;
      }
    },
    fermer() {
      this.ouvert = false;
    },
  },
});

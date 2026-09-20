import { defineStore } from "pinia";

// Système de thèmes (2026-09-09, retour direct de l'utilisateur — "gestion
// des thèmes... ajout mode multi thème professionnel"). "clair" reste le
// thème par défaut, seul documenté par CLAUDE.md §8 (charte visuelle) —
// c'est la seule valeur qui ne pose PAS d'attribut data-theme sur <html>
// (voir appliquer() ci-dessous), donc la seule qui survit si ce store
// n'était jamais appelé pour une raison quelconque.
export const THEMES = [
  { valeur: "clair", libelle: "Clair (par défaut)" },
  { valeur: "sombre", libelle: "Sombre" },
  { valeur: "bleu", libelle: "Bleu professionnel" },
  { valeur: "ardoise", libelle: "Ardoise" },
  { valeur: "emeraude", libelle: "Émeraude" },
];

const CLE_STOCKAGE = "sheq_theme";
const VALEURS_VALIDES = new Set(THEMES.map((t) => t.valeur));

function lire() {
  try {
    const valeur = localStorage.getItem(CLE_STOCKAGE);
    return VALEURS_VALIDES.has(valeur) ? valeur : null;
  } catch {
    return null;
  }
}

function ecrire(valeur) {
  try {
    localStorage.setItem(CLE_STOCKAGE, valeur);
  } catch {
    // Stockage indisponible : le choix ne survit simplement pas au
    // rechargement, pas bloquant pour l'usage courant.
  }
}

export const useThemeStore = defineStore("theme", {
  state: () => ({ theme: lire() ?? "clair" }),

  actions: {
    appliquer(theme) {
      if (!VALEURS_VALIDES.has(theme)) return;
      this.theme = theme;
      ecrire(theme);
      if (theme === "clair") document.documentElement.removeAttribute("data-theme");
      else document.documentElement.setAttribute("data-theme", theme);
    },

    // Appelé une fois au démarrage (main.js) pour que l'attribut posé au
    // tout début du fichier (avant même le montage de Vue, pour éviter un
    // flash du thème par défaut) reste synchronisé avec l'état du store
    // utilisé par le sélecteur.
    initialiser() {
      this.appliquer(this.theme);
    },
  },
});

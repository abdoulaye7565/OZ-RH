import { createPinia, setActivePinia } from "pinia";
import { beforeEach, describe, expect, it } from "vitest";
import { THEMES, useThemeStore } from "./theme";

// Couvre le système de thèmes (2026-09-09, retour direct de l'utilisateur).

beforeEach(() => {
  localStorage.clear();
  document.documentElement.removeAttribute("data-theme");
  setActivePinia(createPinia());
});

describe("appliquer()", () => {
  it("pose l'attribut data-theme pour un thème non clair, et le mémorise", () => {
    const store = useThemeStore();
    store.appliquer("sombre");

    expect(document.documentElement.getAttribute("data-theme")).toBe("sombre");
    expect(store.theme).toBe("sombre");
    expect(localStorage.getItem("sheq_theme")).toBe("sombre");
  });

  it("retire l'attribut pour le thème clair (thème par défaut)", () => {
    document.documentElement.setAttribute("data-theme", "sombre");
    const store = useThemeStore();

    store.appliquer("clair");

    expect(document.documentElement.hasAttribute("data-theme")).toBe(false);
    expect(store.theme).toBe("clair");
  });

  it("ignore une valeur de thème invalide, sans toucher à l'état actuel", () => {
    const store = useThemeStore();
    store.appliquer("ardoise");

    store.appliquer("inexistant");

    expect(store.theme).toBe("ardoise");
    expect(document.documentElement.getAttribute("data-theme")).toBe("ardoise");
  });

  it("couvre les 5 thèmes déclarés", () => {
    expect(THEMES.map((t) => t.valeur)).toEqual(["clair", "sombre", "bleu", "ardoise", "emeraude"]);
  });
});

describe("état initial", () => {
  it("démarre sur clair si rien n'est mémorisé", () => {
    const store = useThemeStore();
    expect(store.theme).toBe("clair");
  });

  it("reprend le thème mémorisé au démarrage", () => {
    localStorage.setItem("sheq_theme", "emeraude");
    const store = useThemeStore();
    expect(store.theme).toBe("emeraude");
  });

  it("ignore une valeur mémorisée invalide (donnée corrompue) et retombe sur clair", () => {
    localStorage.setItem("sheq_theme", "valeur-qui-nexiste-pas");
    const store = useThemeStore();
    expect(store.theme).toBe("clair");
  });
});

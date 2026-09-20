import { nextTick, ref } from "vue";
import { describe, expect, it } from "vitest";
import { useRechercheEtPagination } from "./useRechercheEtPagination";

// 2026-09-09, retour direct de l'utilisateur — "les listes doivent avoir une
// possibilité de recherche, les listes doivent être paginées".

function liste(n) {
  return Array.from({ length: n }, (_, i) => ({ id: i + 1, nom: `Élément ${i + 1}` }));
}

describe("useRechercheEtPagination()", () => {
  it("découpe la liste source en pages de la taille demandée", () => {
    const source = ref(liste(25));
    const { elementsPage, totalPages } = useRechercheEtPagination(source, () => true, 10);
    expect(elementsPage.value).toHaveLength(10);
    expect(elementsPage.value[0].id).toBe(1);
    expect(totalPages.value).toBe(3);
  });

  it("allerPage() change la page affichée et reste dans les bornes", () => {
    const source = ref(liste(25));
    const { elementsPage, page, allerPage } = useRechercheEtPagination(source, () => true, 10);
    allerPage(3);
    expect(page.value).toBe(3);
    expect(elementsPage.value).toHaveLength(5); // dernière page, 25 - 20

    allerPage(99); // au-delà du total : plafonné
    expect(page.value).toBe(3);
    allerPage(0); // en dessous de 1 : plancher
    expect(page.value).toBe(1);
  });

  it("filtre selon le prédicat fourni et repasse en page 1", async () => {
    const source = ref(liste(25));
    const filtrer = (item, terme) => item.nom.toLowerCase().includes(terme);
    const { recherche, resultats, elementsPage, page, allerPage, totalPages } =
      useRechercheEtPagination(source, filtrer, 10);

    allerPage(2);
    expect(page.value).toBe(2);

    recherche.value = "Élément 1"; // matche "Élément 1" et "Élément 10"-"19" : 11 éléments
    await nextTick();

    expect(page.value).toBe(1); // remis à 1 par la nouvelle recherche
    expect(resultats.value.length).toBe(11);
    expect(totalPages.value).toBe(2);
    expect(elementsPage.value.every((i) => i.nom.includes("1"))).toBe(true);
  });

  it("une recherche vide (espaces) équivaut à aucun filtre", async () => {
    const source = ref(liste(5));
    const { recherche, resultats } = useRechercheEtPagination(source, () => false, 10);
    recherche.value = "   ";
    await nextTick();
    expect(resultats.value).toHaveLength(5); // filtrer() jamais appelé, terme vide
  });

  it("un prédicat qui coerce un champ numérique en chaîne filtre correctement", async () => {
    // Régression : `numero` est un entier côté API. Un prédicat qui fait
    // `r.numero.toLowerCase()` lève et casse silencieusement la recherche —
    // le prédicat doit passer par String(). Ici on vérifie qu'un prédicat
    // correct (avec String()) fonctionne sur un champ numérique.
    const source = ref([
      { id: 1, numero: 12, danger: "Feu" },
      { id: 2, numero: 34, danger: "Chute" },
    ]);
    const filtrer = (r, terme) => String(r.numero).includes(terme) || r.danger.toLowerCase().includes(terme);
    const { recherche, resultats } = useRechercheEtPagination(source, filtrer, 10);

    recherche.value = "12";
    await nextTick();
    expect(resultats.value).toHaveLength(1);
    expect(resultats.value[0].id).toBe(1);
  });

  it("reste dans les bornes si la liste source rétrécit (ex. archivage)", async () => {
    const source = ref(liste(15));
    const { page, allerPage, totalPages } = useRechercheEtPagination(source, () => true, 10);
    allerPage(2);
    expect(page.value).toBe(2);

    source.value = liste(3); // 1 seule page désormais
    await nextTick();

    expect(totalPages.value).toBe(1);
    expect(page.value).toBe(1);
  });
});

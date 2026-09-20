import { computed, ref, watch } from "vue";

/**
 * Recherche texte + pagination côté client, pour les listes des écrans
 * desktop (2026-09-09, retour direct de l'utilisateur — "les listes doivent
 * avoir une possibilité de recherche, les listes doivent être paginées").
 *
 * Toutes les listes de l'application sont chargées en entier par leur store
 * (Pinia) au montage — il n'y a pas de pagination côté serveur aujourd'hui,
 * et les volumes réels (quelques centaines de lignes maximum, cf. CDC) ne la
 * justifient pas. Ce composable filtre et découpe donc côté client la liste
 * déjà en mémoire ; il ne fait aucun appel réseau. S'il fallait un jour
 * paginer côté serveur (très gros volumes), l'API de ce composable resterait
 * la même côté vue, seule son implémentation interne changerait.
 *
 * ATTENTION : `filtrer` ne doit jamais lever d'exception. S'il en lève une
 * (typiquement `.toLowerCase()` appelé sur un champ numérique — un `numero`
 * renvoyé par l'API est un entier, pas une chaîne), le getter de `resultats`
 * lève à son tour et Vue interrompt silencieusement la chaîne réactive : la
 * recherche cesse de fonctionner sans la moindre erreur en console. Coercer
 * chaque champ avec `String(x ?? "")` avant `.toLowerCase()`.
 *
 * @param {import('vue').Ref<any[]>|import('vue').ComputedRef<any[]>} source - liste source (déjà triée si besoin par l'appelant)
 * @param {(item: any, terme: string) => boolean} filtrer - prédicat de recherche ; `terme` est déjà passé en minuscules et sans espaces superflus. NE DOIT PAS LEVER.
 * @param {number} [parPage] - taille de page, 10 par défaut
 */
export function useRechercheEtPagination(source, filtrer, parPage = 10) {
  const recherche = ref("");
  const page = ref(1);

  const resultats = computed(() => {
    const terme = recherche.value.trim().toLowerCase();
    if (!terme) return source.value;
    return source.value.filter((item) => filtrer(item, terme));
  });

  const totalPages = computed(() => Math.max(1, Math.ceil(resultats.value.length / parPage)));

  const elementsPage = computed(() =>
    resultats.value.slice((page.value - 1) * parPage, page.value * parPage)
  );

  // Revenir en page 1 à chaque nouvelle recherche...
  watch(recherche, () => {
    page.value = 1;
  });
  // ...et rester dans les bornes si la liste rétrécit pendant qu'on est sur
  // une page haute (ex. un archivage fait passer un écran de 3 pages à 1).
  watch(totalPages, (n) => {
    if (page.value > n) page.value = n;
  });

  function allerPage(n) {
    page.value = Math.min(Math.max(1, n), totalPages.value);
  }

  return { recherche, page, totalPages, resultats, elementsPage, allerPage };
}

<script setup>
/**
 * Pied de tableau desktop : décompte + numéros de page.
 * Reprend `.pagin`/`.pg`/`.pg button.on`, présent dans style.css depuis
 * l'import de la maquette mais jamais câblé avant ce chantier — voir
 * composables/useRechercheEtPagination.js (2026-09-09).
 *
 * Le texte de décompte (ex. "12 sur 40 risques affichés") reste au choix de
 * l'écran appelant, via le slot par défaut : il varie trop d'un module à
 * l'autre (nom des entités) pour être générique ici.
 */
defineProps({
  page: { type: Number, required: true },
  totalPages: { type: Number, required: true },
});
const emit = defineEmits(["changer"]);

// Fenêtre de numéros affichés autour de la page courante, avec "…" pour les
// trous — au-delà de 7 pages, afficher tous les numéros surchargerait la
// barre (même logique que la maquette, qui montre déjà un "…" statique).
function pagesAffichees(page, total) {
  if (total <= 7) return Array.from({ length: total }, (_, i) => i + 1);
  const bornes = new Set([1, total, page]);
  if (page > 1) bornes.add(page - 1);
  if (page < total) bornes.add(page + 1);
  const nums = [...bornes].sort((a, b) => a - b);
  const out = [];
  for (let i = 0; i < nums.length; i++) {
    if (i > 0 && nums[i] - nums[i - 1] > 1) out.push("…");
    out.push(nums[i]);
  }
  return out;
}
</script>

<template>
  <div class="pagin">
    <span><slot /></span>
    <div class="pg" v-if="totalPages > 1">
      <button
        v-for="(p, i) in pagesAffichees(page, totalPages)"
        :key="i"
        :class="{ on: p === page }"
        :disabled="p === '…'"
        @click="p !== '…' && emit('changer', p)"
      >{{ p }}</button>
    </div>
  </div>
</template>

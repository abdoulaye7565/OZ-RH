<script setup>
/**
 * Fenêtre modale générique (2026-09-09, retour direct de l'utilisateur —
 * "gestion des dropdown pour les formulaires d'inscription", précisé en
 * échange : une vraie fenêtre modale centrée, pas un panneau ancré au
 * bouton). Remplace le motif "carte affichée en haut de la page" utilisé
 * jusqu'ici par une vingtaine d'écrans.
 *
 * Se ferme sur Échap, sur clic hors de la boîte, ou via le bouton ✕ — jamais
 * sur un clic À L'INTÉRIEUR de la boîte (@click.self, pas @click, sur le
 * fond). Le contenu reste à la charge de l'écran appelant, via un slot.
 *
 * Accessibilité clavier (revue d'ensemble 2026-09-10) : au montage, le focus
 * passe dans la modale (premier champ focalisable, sinon la boîte) ; la
 * touche Tab est piégée à l'intérieur (on ne peut pas tabuler vers la page
 * derrière) ; au démontage, le focus revient sur l'élément qui avait ouvert
 * la modale.
 */
import { nextTick, onBeforeUnmount, onMounted, ref } from "vue";
import Icone from "./Icone.vue";

defineProps({ titre: { type: String, required: true } });
const emit = defineEmits(["fermer"]);

const boite = ref(null);
let elementAvant = null;

const SELECTEUR_FOCUS =
  'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])';

function elementsFocalisables() {
  return boite.value ? [...boite.value.querySelectorAll(SELECTEUR_FOCUS)].filter((el) => el.offsetParent !== null) : [];
}

function surClavier(e) {
  if (e.key === "Escape") {
    emit("fermer");
    return;
  }
  if (e.key !== "Tab" || !boite.value) return;
  const focalisables = elementsFocalisables();
  if (!focalisables.length) {
    e.preventDefault();
    boite.value.focus();
    return;
  }
  const premier = focalisables[0];
  const dernier = focalisables[focalisables.length - 1];
  const actif = document.activeElement;
  if (e.shiftKey && (actif === premier || !boite.value.contains(actif))) {
    e.preventDefault();
    dernier.focus();
  } else if (!e.shiftKey && actif === dernier) {
    e.preventDefault();
    premier.focus();
  }
}

onMounted(async () => {
  elementAvant = document.activeElement;
  document.addEventListener("keydown", surClavier, true);
  await nextTick();
  const focalisables = elementsFocalisables();
  (focalisables[0] ?? boite.value)?.focus();
});

onBeforeUnmount(() => {
  document.removeEventListener("keydown", surClavier, true);
  // Rendre le focus à l'élément déclencheur s'il est toujours dans le DOM.
  if (elementAvant && document.contains(elementAvant)) elementAvant.focus();
});
</script>

<template>
  <div class="modal-fond" @click.self="emit('fermer')">
    <div ref="boite" class="modal-boite card" role="dialog" aria-modal="true" :aria-label="titre" tabindex="-1">
      <div class="ch">
        <h3>{{ titre }}</h3>
        <button class="modal-x" type="button" aria-label="Fermer" @click="emit('fermer')">
          <Icone nom="x" taille="sm" />
        </button>
      </div>
      <div class="cb"><slot /></div>
    </div>
  </div>
</template>

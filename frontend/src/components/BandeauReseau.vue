<script setup>
/**
 * Bandeau d'état réseau (maquette : classe .net). Reflète l'état réel du
 * navigateur (navigator.onLine + événements online/offline).
 *
 * Le compteur "N éléments en attente" de la maquette suppose une file d'attente
 * de synchronisation hors connexion : mécanisme construit le 2026-09-08 (voir
 * stores/horsConnexion.js, services/filesync.js), affiché ici réellement —
 * plus une simple valeur fixe.
 */
import { computed, onBeforeUnmount, onMounted, ref } from "vue";
import Icone from "./Icone.vue";
import { useHorsConnexionStore } from "../stores/horsConnexion";

const horsConnexion = useHorsConnexionStore();
const enLigne = ref(navigator.onLine);

function majEtat() {
  enLigne.value = navigator.onLine;
  horsConnexion.rafraichirCompte();
}

onMounted(() => {
  window.addEventListener("online", majEtat);
  window.addEventListener("offline", majEtat);
  horsConnexion.rafraichirCompte();
});
onBeforeUnmount(() => {
  window.removeEventListener("online", majEtat);
  window.removeEventListener("offline", majEtat);
});

// Sous-texte de droite (maquette : classe .sp) — même vocabulaire que
// #s-newsig/#p-slam/#p-parc dans la maquette ("N éléments en attente",
// "Synchronisé à l'instant"), calculé ici réellement plutôt que fixé en dur.
const sousTexte = computed(() => {
  if (!enLigne.value) {
    if (horsConnexion.compteEnAttente) {
      return `${horsConnexion.compteEnAttente} élément${horsConnexion.compteEnAttente > 1 ? "s" : ""} en attente`;
    }
    return null;
  }
  if (horsConnexion.synchronisationEnCours) return "Synchronisation…";
  if (horsConnexion.derniereSynchronisation) {
    const secondes = (Date.now() - new Date(horsConnexion.derniereSynchronisation).getTime()) / 1000;
    if (secondes < 60) return "Synchronisé à l'instant";
    return `Synchronisé il y a ${Math.round(secondes / 60)} min`;
  }
  return null;
});
</script>

<template>
  <div class="net" :class="enLigne ? 'online' : 'offline'">
    <Icone :nom="enLigne ? 'wifi' : 'wifioff'" taille="sm" />
    {{ enLigne ? "En ligne" : "Hors connexion" }}
    <span v-if="sousTexte" class="sp">{{ sousTexte }}</span>
  </div>
</template>

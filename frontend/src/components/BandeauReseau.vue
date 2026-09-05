<script setup>
/**
 * Bandeau d'état réseau (maquette : classe .net). Reflète l'état réel du
 * navigateur (navigator.onLine + événements online/offline).
 *
 * Le compteur "N éléments en attente" de la maquette suppose une file d'attente
 * de synchronisation hors connexion : ce mécanisme est le prompt 1.4, pas
 * celui-ci. Tant qu'il n'existe pas, ce bandeau affiche seulement l'état de
 * connexion, sans jamais annoncer une synchronisation qui n'a pas lieu.
 */
import { onBeforeUnmount, onMounted, ref } from "vue";
import Icone from "./Icone.vue";

const enLigne = ref(navigator.onLine);

function majEtat() {
  enLigne.value = navigator.onLine;
}

onMounted(() => {
  window.addEventListener("online", majEtat);
  window.addEventListener("offline", majEtat);
});
onBeforeUnmount(() => {
  window.removeEventListener("online", majEtat);
  window.removeEventListener("offline", majEtat);
});
</script>

<template>
  <div class="net" :class="enLigne ? 'online' : 'offline'">
    <Icone :nom="enLigne ? 'wifi' : 'wifioff'" taille="sm" />
    {{ enLigne ? "En ligne" : "Hors connexion" }}
  </div>
</template>

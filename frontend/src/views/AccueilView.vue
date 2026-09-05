<script setup>
import { onMounted, ref } from "vue";
import api from "../services/api";

const etatApi = ref("verification");
const environnement = ref("");

onMounted(async () => {
  try {
    const reponse = await api.getHealth();
    etatApi.value = reponse.status === "ok" ? "connectee" : "erreur";
    environnement.value = reponse.environment ?? "";
  } catch {
    etatApi.value = "injoignable";
  }
});
</script>

<template>
  <main class="accueil">
    <h1>SHEQ Management</h1>
    <p>Squelette d'application initialisé — aucun module métier encore implémenté.</p>
    <p class="etat" :class="etatApi">
      API : <strong>{{ etatApi }}</strong>
      <span v-if="environnement"> ({{ environnement }})</span>
    </p>
  </main>
</template>

<style scoped>
.accueil {
  max-width: 640px;
  margin: 10vh auto;
  padding: 32px;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--r-lg);
  box-shadow: var(--sh);
  text-align: center;
}

h1 {
  color: var(--navy);
  margin: 0 0 8px;
}

.etat {
  font-weight: 650;
}

.etat.connectee {
  color: var(--green);
}

.etat.erreur,
.etat.injoignable {
  color: var(--red);
}
</style>

<script setup>
/**
 * Écran de connexion — ajouté par nécessité (voir stores/auth.js), pas demandé
 * par un prompt précis du lotissement. Reprend le contenu de la maquette
 * (écran "s-login") sans prétendre en être une implémentation officiellement
 * spécifiée.
 */
import { ref } from "vue";
import { useRouter } from "vue-router";
import Icone from "../components/Icone.vue";
import { useAuthStore } from "../stores/auth";

const auth = useAuthStore();
const router = useRouter();

const identifiant = ref("");
const motDePasse = ref("");

async function seConnecter() {
  const ok = await auth.connecter(identifiant.value, motDePasse.value);
  if (ok) router.push({ name: "signalements" });
}
</script>

<template>
  <div class="ecran-mobile">
    <div class="login">
      <div class="mk"><Icone nom="hirondelle" taille="lg" /></div>
      <h2>SHEQ Management</h2>
      <p class="sb">Hirondelles IT Lab</p>

      <label class="f" for="identifiant">Identifiant</label>
      <input
        id="identifiant"
        v-model="identifiant"
        class="inp"
        autocomplete="username"
        @keyup.enter="seConnecter"
      />

      <label class="f" for="mot-de-passe">Mot de passe</label>
      <input
        id="mot-de-passe"
        v-model="motDePasse"
        class="inp"
        type="password"
        autocomplete="current-password"
        @keyup.enter="seConnecter"
      />

      <div style="height: 18px"></div>
      <button class="btn pri" :disabled="auth.enCours" @click="seConnecter">
        {{ auth.enCours ? "Connexion…" : "Se connecter" }}
      </button>

      <div v-if="auth.erreur" class="banner err" style="margin-top: 16px">{{ auth.erreur }}</div>
      <div class="banner info" style="margin-top: 16px">
        <div>Le mode hors connexion n'est pas encore actif : une connexion réseau est nécessaire pour se connecter et pour enregistrer vos saisies.</div>
      </div>
    </div>
  </div>
</template>

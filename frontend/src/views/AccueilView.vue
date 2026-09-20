<script setup>
/**
 * Écran d'accueil — amélioré le 2026-09-09 (retour direct de l'utilisateur :
 * "l'écran d'entrée de l'application doit être amélioré").
 *
 * Double rôle, pas différencié jusqu'ici — ce qui posait exactement le
 * problème signalé : cet écran est à la fois (a) la page d'accueil avant
 * connexion (première impression de l'application) et (b) la destination du
 * bouton "Accueil" de la barre d'onglets, présente sur ~19 écrans mobiles,
 * pour un utilisateur déjà connecté. La version précédente traitait
 * toujours le cas (a), même pour un utilisateur déjà connecté qui cliquait
 * sur "Accueil" depuis un écran profond — renvoyé vers une page d'accueil
 * générique plutôt que ramené à son usage courant. Corrigé : un utilisateur
 * déjà connecté est redirigé vers Signalements (même destination que juste
 * après connexion, ConnexionView.vue) — "Accueil" ramène à l'écran de
 * départ réel, pas à une vitrine.
 *
 * Contenu avant connexion retravaillé : le texte d'état brut de l'API
 * ("API : connectee (development)") n'avait pas sa place devant un
 * utilisateur — jargon de développement, pas une information utile pour
 * lui. Remplacé par le même indicateur réseau que le reste de
 * l'application (BandeauReseau.vue), déjà utilisé partout ailleurs mais
 * absent jusqu'ici du tout premier écran vu.
 */
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import BandeauReseau from "../components/BandeauReseau.vue";
import Icone from "../components/Icone.vue";
import { useAuthStore } from "../stores/auth";

const auth = useAuthStore();
const router = useRouter();
const pretAAfficher = ref(false);

onMounted(() => {
  if (auth.estConnecte) {
    router.replace({ name: "signalements" });
    return;
  }
  pretAAfficher.value = true;
});
</script>

<template>
  <div v-if="pretAAfficher" class="ecran-mobile">
    <BandeauReseau />
    <main class="accueil">
      <div class="mk"><Icone nom="hirondelle" taille="xl" /></div>
      <h1>SHEQ Management</h1>
      <p class="sb">Hirondelles IT Lab — Sécurité, Santé, Environnement, Qualité</p>
      <RouterLink class="btn pri" style="margin-top: 22px" to="/connexion">
        Se connecter
        <Icone nom="chev" taille="sm" />
      </RouterLink>
    </main>
  </div>
</template>

<style scoped>
.accueil {
  max-width: 420px;
  margin: 14vh auto 0;
  padding: 0 28px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.accueil .mk {
  width: 64px;
  height: 64px;
  border-radius: 16px;
  background: linear-gradient(140deg, #f0c63e, #b8901b);
  color: var(--navy);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 18px;
}
h1 {
  color: var(--navy);
  font-size: 22px;
  letter-spacing: -0.3px;
  margin: 0 0 6px;
}
.sb {
  color: var(--mut);
  font-size: 13px;
  line-height: 1.5;
  margin: 0;
}
.btn.pri {
  width: auto;
  padding: 0 24px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  text-decoration: none;
}
</style>

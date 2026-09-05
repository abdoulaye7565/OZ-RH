import { createRouter, createWebHistory } from "vue-router";
import AccueilView from "../views/AccueilView.vue";
import ConnexionView from "../views/ConnexionView.vue";
import NouveauSignalementView from "../views/NouveauSignalementView.vue";
import SignalementsView from "../views/SignalementsView.vue";
import { useAuthStore } from "../stores/auth";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: "/", name: "accueil", component: AccueilView },
    { path: "/connexion", name: "connexion", component: ConnexionView },
    {
      path: "/signalements",
      name: "signalements",
      component: SignalementsView,
      meta: { necessiteAuth: true },
    },
    {
      path: "/signalements/nouveau",
      name: "nouveau-signalement",
      component: NouveauSignalementView,
      meta: { necessiteAuth: true },
    },
  ],
});

router.beforeEach((to) => {
  const auth = useAuthStore();
  if (to.meta.necessiteAuth && !auth.estConnecte) {
    return { name: "connexion" };
  }
  return true;
});

export default router;

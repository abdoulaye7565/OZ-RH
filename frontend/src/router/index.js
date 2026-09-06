import { createRouter, createWebHistory } from "vue-router";
import AccueilView from "../views/AccueilView.vue";
import ConnexionView from "../views/ConnexionView.vue";
import NouveauSignalementView from "../views/NouveauSignalementView.vue";
import SignalementsView from "../views/SignalementsView.vue";
import TableauBordMobileView from "../views/TableauBordMobileView.vue";
import TableauBordDesktopView from "../views/TableauBordDesktopView.vue";
import SlamView from "../views/SlamView.vue";
import PermisValidationView from "../views/PermisValidationView.vue";
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
    {
      path: "/tableau-de-bord",
      name: "tableau-de-bord",
      component: TableauBordMobileView,
      meta: { necessiteAuth: true },
    },
    {
      path: "/slam",
      name: "slam",
      component: SlamView,
      meta: { necessiteAuth: true },
    },
    {
      path: "/permis/:id/validation",
      name: "permis-validation",
      component: PermisValidationView,
      meta: { necessiteAuth: true },
    },
    // Préfixe /gestion : amorce de l'interface de gestion desktop (CDC 11.1,
    // "deux interfaces, deux usages"). Une seule page pour l'instant.
    {
      path: "/gestion/tableau-de-bord",
      name: "gestion-tableau-de-bord",
      component: TableauBordDesktopView,
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

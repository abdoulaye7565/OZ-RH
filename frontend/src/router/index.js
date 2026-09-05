import { createRouter, createWebHistory } from "vue-router";
import AccueilView from "../views/AccueilView.vue";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [{ path: "/", name: "accueil", component: AccueilView }],
});

export default router;

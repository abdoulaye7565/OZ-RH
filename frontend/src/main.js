import { createApp } from "vue";
import { createPinia } from "pinia";
import "./style.css";
import App from "./App.vue";
import router from "./router";
import api from "./services/api";
import { useAuthStore } from "./stores/auth";
import { useHorsConnexionStore } from "./stores/horsConnexion";
import { useSignalementsStore } from "./stores/signalements";

const app = createApp(App);

app.use(createPinia());
app.use(router);

// Rafraîchissement du jeton (2026-09-08, voir services/api.js) : si le
// refresh token a lui aussi expiré (ou n'existe pas), la session est
// vraiment finie — on nettoie l'état local et on renvoie vers /connexion,
// plutôt que de laisser chaque écran échouer séparément sur un 401.
const auth = useAuthStore();
api.definirGestionnaireSessionExpiree(() => {
  auth.deconnecter();
  if (router.currentRoute.value.name !== "connexion") {
    router.push({ name: "connexion" });
  }
});

// Câblage de la synchronisation hors connexion (voir stores/horsConnexion.js) :
// fait ici, une seule fois au démarrage, pour que les stores métier n'aient
// jamais besoin de s'importer entre eux.
const horsConnexion = useHorsConnexionStore();
const signalements = useSignalementsStore();
horsConnexion.enregistrerGestionnaire("signalement", {
  executer: (champs, fichiers) => signalements.envoyerVersServeur(champs, fichiers),
  onSucces: () => signalements.charger(),
});
horsConnexion.demarrerEcouteReseau();
horsConnexion.rafraichirCompte();
// Au cas où l'app démarre déjà en ligne avec des éléments laissés en attente
// d'une session hors connexion précédente (onglet fermé avant le retour du
// réseau) : on tente une synchronisation dès le démarrage, pas seulement à
// l'événement "online" (qui ne se déclenchera pas si on était déjà en ligne).
horsConnexion.synchroniser();

app.mount("#app");

import { createApp } from "vue";
import { createPinia } from "pinia";
import "./style.css";
import App from "./App.vue";
import router from "./router";
import api from "./services/api";
import { useAuthStore } from "./stores/auth";
import { useHorsConnexionStore } from "./stores/horsConnexion";
import { useSignalementsStore } from "./stores/signalements";
import { useInspectionsStore } from "./stores/inspections";
import { useThemeStore } from "./stores/theme";

// Thème posé ici, avant même la création de l'app Vue (2026-09-09, voir
// stores/theme.js) : évite un flash visible du thème clair par défaut avant
// que Pinia n'ait eu le temps de lire le thème mémorisé.
try {
  const themeStocke = localStorage.getItem("sheq_theme");
  if (themeStocke && themeStocke !== "clair") document.documentElement.setAttribute("data-theme", themeStocke);
} catch {
  // Stockage indisponible : reste sur le thème clair par défaut.
}

const app = createApp(App);

app.use(createPinia());
app.use(router);

useThemeStore().initialiser();

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
// SLAM (2026-09-09) : pas de store dédié (SlamView.vue appelle l'API
// directement, prompt 2.2) et rien à rafraîchir après coup — l'écran affiche
// le verdict localement dès la décision prise, sans dépendre de sa
// confirmation serveur. Pas d'onSucces, volontairement.
horsConnexion.enregistrerGestionnaire("slam", {
  executer: (champs) => api.requete("/api/v1/slam", { methode: "POST", corps: champs }),
});
// Inspections (2026-09-09) : flux en plusieurs étapes dépendantes côté
// serveur (créer → coter des points → clôturer) — voir le commentaire
// d'en-tête de stores/inspections.js pour le détail du mécanisme
// (_mettreEnFile). `champs.id === null` signifie que l'inspection n'a
// jamais été créée côté serveur : le POST initial l'emporte, PATCH/clôture
// ne s'appliquent qu'ensuite, sur l'id réel obtenu.
const inspections = useInspectionsStore();
horsConnexion.enregistrerGestionnaire("inspection", {
  executer: async (champs) => {
    let id = champs.id;
    if (id === null) {
      const inspection = await api.requete("/api/v1/inspections", {
        methode: "POST",
        corps: { ...champs.donnees_creation, points: champs.points },
      });
      id = inspection.id;
    } else if (champs.points) {
      await api.requete(`/api/v1/inspections/${id}/points`, { methode: "PATCH", corps: { points: champs.points } });
    }
    if (champs.cloturer) {
      await api.requete(`/api/v1/inspections/${id}/cloturer`, { methode: "POST" });
    }
  },
  onSucces: () => inspections.charger(),
});
horsConnexion.demarrerEcouteReseau();
horsConnexion.rafraichirCompte();
// Au cas où l'app démarre déjà en ligne avec des éléments laissés en attente
// d'une session hors connexion précédente (onglet fermé avant le retour du
// réseau) : on tente une synchronisation dès le démarrage, pas seulement à
// l'événement "online" (qui ne se déclenchera pas si on était déjà en ligne).
horsConnexion.synchroniser();

app.mount("#app");

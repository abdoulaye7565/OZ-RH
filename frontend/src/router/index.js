import { createRouter, createWebHistory } from "vue-router";
import AccueilView from "../views/AccueilView.vue";
import ConnexionView from "../views/ConnexionView.vue";
import NouveauSignalementView from "../views/NouveauSignalementView.vue";
import SignalementsView from "../views/SignalementsView.vue";
import SignalementDetailView from "../views/SignalementDetailView.vue";
import TableauBordMobileView from "../views/TableauBordMobileView.vue";
import TableauBordDesktopView from "../views/TableauBordDesktopView.vue";
import SlamView from "../views/SlamView.vue";
import PermisValidationView from "../views/PermisValidationView.vue";
import AssistantDocumentaireView from "../views/AssistantDocumentaireView.vue";
import AssistantDocumentaireDesktopView from "../views/AssistantDocumentaireDesktopView.vue";
import MenuView from "../views/MenuView.vue";
import EpiView from "../views/EpiView.vue";
import EpiDesktopView from "../views/EpiDesktopView.vue";
import RisquesView from "../views/RisquesView.vue";
import RisquesDesktopView from "../views/RisquesDesktopView.vue";
import ActionsView from "../views/ActionsView.vue";
import ActionsDesktopView from "../views/ActionsDesktopView.vue";
import ParcView from "../views/ParcView.vue";
import ParcFicheView from "../views/ParcFicheView.vue";
import ParcDesktopView from "../views/ParcDesktopView.vue";
import FormationsView from "../views/FormationsView.vue";
import FormationsDesktopView from "../views/FormationsDesktopView.vue";
import AuditsView from "../views/AuditsView.vue";
import AuditsDesktopView from "../views/AuditsDesktopView.vue";
import DocumentsView from "../views/DocumentsView.vue";
import DocumentsDossierView from "../views/DocumentsDossierView.vue";
import DocumentsDesktopView from "../views/DocumentsDesktopView.vue";
import VisiteursView from "../views/VisiteursView.vue";
import VisiteursDesktopView from "../views/VisiteursDesktopView.vue";
import DechetsView from "../views/DechetsView.vue";
import DechetsDesktopView from "../views/DechetsDesktopView.vue";
import SatisfactionQuestionnaireView from "../views/SatisfactionQuestionnaireView.vue";
import SatisfactionDesktopView from "../views/SatisfactionDesktopView.vue";
import PermisView from "../views/PermisView.vue";
import PermisDesktopView from "../views/PermisDesktopView.vue";
import UtilisateursDesktopView from "../views/UtilisateursDesktopView.vue";
import SitesDesktopView from "../views/SitesDesktopView.vue";
import ParametresDesktopView from "../views/ParametresDesktopView.vue";
import InspectionsView from "../views/InspectionsView.vue";
import CoffreFortView from "../views/CoffreFortView.vue";
import CoffreFortDesktopView from "../views/CoffreFortDesktopView.vue";
import InspectionDetailView from "../views/InspectionDetailView.vue";
import InspectionsDesktopView from "../views/InspectionsDesktopView.vue";
import GestionLayout from "../views/GestionLayout.vue";
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
      path: "/signalements/:id",
      name: "signalement-detail",
      component: SignalementDetailView,
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
    {
      path: "/assistant",
      name: "assistant-documentaire",
      component: AssistantDocumentaireView,
      meta: { necessiteAuth: true },
    },
    {
      path: "/menu",
      name: "menu",
      component: MenuView,
      meta: { necessiteAuth: true },
    },
    {
      path: "/epi",
      name: "epi",
      component: EpiView,
      meta: { necessiteAuth: true },
    },
    {
      path: "/risques",
      name: "risques",
      component: RisquesView,
      meta: { necessiteAuth: true },
    },
    {
      path: "/actions",
      name: "actions",
      component: ActionsView,
      meta: { necessiteAuth: true },
    },
    {
      path: "/parc",
      name: "parc",
      component: ParcView,
      meta: { necessiteAuth: true },
    },
    {
      path: "/parc/:id",
      name: "parc-fiche",
      component: ParcFicheView,
      meta: { necessiteAuth: true },
    },
    {
      path: "/formations",
      name: "formations",
      component: FormationsView,
      meta: { necessiteAuth: true },
    },
    {
      path: "/audits",
      name: "audits",
      component: AuditsView,
      meta: { necessiteAuth: true },
    },
    {
      path: "/documents",
      name: "documents",
      component: DocumentsView,
      meta: { necessiteAuth: true },
    },
    {
      path: "/documents/:dossier",
      name: "documents-dossier",
      component: DocumentsDossierView,
      meta: { necessiteAuth: true },
    },
    {
      path: "/visiteurs",
      name: "visiteurs",
      component: VisiteursView,
      meta: { necessiteAuth: true },
    },
    {
      path: "/dechets",
      name: "dechets",
      component: DechetsView,
      meta: { necessiteAuth: true },
    },
    {
      path: "/permis",
      name: "permis-liste",
      component: PermisView,
      meta: { necessiteAuth: true },
    },
    {
      path: "/inspections",
      name: "inspections",
      component: InspectionsView,
      meta: { necessiteAuth: true },
    },
    {
      path: "/coffre-fort",
      name: "coffre-fort",
      component: CoffreFortView,
      meta: { necessiteAuth: true },
    },
    // Déclarée avant /inspections/:id : une route statique ("nouvelle") doit
    // être mise en correspondance avant le segment dynamique qui, sinon, la
    // capturerait comme un identifiant.
    {
      path: "/inspections/nouvelle",
      name: "inspection-nouvelle",
      component: InspectionDetailView,
      meta: { necessiteAuth: true },
    },
    {
      path: "/inspections/:id",
      name: "inspection-detail",
      component: InspectionDetailView,
      meta: { necessiteAuth: true },
    },
    // Route publique volontairement : questionnaire client accessible par lien
    // (jeton), sans compte — voir schemas/satisfaction.py, QuestionnaireSortie.
    {
      path: "/satisfaction/:jeton",
      name: "satisfaction-questionnaire",
      component: SatisfactionQuestionnaireView,
    },
    // Préfixe /gestion : interface de gestion desktop (CDC 11.1, "deux
    // interfaces, deux usages") — ossature commune (barre latérale,
    // GestionLayout.vue) partagée par tous les écrans desktop.
    {
      path: "/gestion",
      component: GestionLayout,
      meta: { necessiteAuth: true },
      children: [
        { path: "tableau-de-bord", name: "gestion-tableau-de-bord", component: TableauBordDesktopView, meta: { titre: "Tableau de bord" } },
        { path: "assistant", name: "gestion-assistant-documentaire", component: AssistantDocumentaireDesktopView, meta: { titre: "Assistant documentaire" } },
        { path: "epi", name: "gestion-epi", component: EpiDesktopView, meta: { titre: "EPI antichute" } },
        { path: "risques", name: "gestion-risques", component: RisquesDesktopView, meta: { titre: "Registre des risques" } },
        { path: "actions", name: "gestion-actions", component: ActionsDesktopView, meta: { titre: "Plan d'action" } },
        { path: "parc", name: "gestion-parc", component: ParcDesktopView, meta: { titre: "Parc & configurations" } },
        { path: "formations", name: "gestion-formations", component: FormationsDesktopView, meta: { titre: "Formations" } },
        { path: "audits", name: "gestion-audits", component: AuditsDesktopView, meta: { titre: "Audits & revues" } },
        { path: "documents", name: "gestion-documents", component: DocumentsDesktopView, meta: { titre: "Documents" } },
        { path: "visiteurs", name: "gestion-visiteurs", component: VisiteursDesktopView, meta: { titre: "Visiteurs" } },
        { path: "dechets", name: "gestion-dechets", component: DechetsDesktopView, meta: { titre: "Déchets & environnement" } },
        { path: "satisfaction", name: "gestion-satisfaction", component: SatisfactionDesktopView, meta: { titre: "Satisfaction client" } },
        { path: "permis", name: "gestion-permis", component: PermisDesktopView, meta: { titre: "SLAM & permis" } },
        { path: "utilisateurs", name: "gestion-utilisateurs", component: UtilisateursDesktopView, meta: { titre: "Utilisateurs & rôles" } },
        { path: "sites", name: "gestion-sites", component: SitesDesktopView, meta: { titre: "Sites" } },
        { path: "parametres", name: "gestion-parametres", component: ParametresDesktopView, meta: { titre: "Paramètres" } },
        { path: "inspections", name: "gestion-inspections", component: InspectionsDesktopView, meta: { titre: "Inspections" } },
        { path: "coffre-fort", name: "gestion-coffre-fort", component: CoffreFortDesktopView, meta: { titre: "Coffre-fort" } },
      ],
    },
  ],
});

router.beforeEach(async (to) => {
  const auth = useAuthStore();
  if (to.meta.necessiteAuth && !auth.estConnecte) {
    return { name: "connexion" };
  }
  // `utilisateur` ne survit pas à un rechargement de page (seul `jeton` est
  // persisté, voir stores/auth.js) : sans ceci, tout écran qui lit
  // auth.utilisateur.role juste après un rechargement le trouve à `null`.
  if (auth.estConnecte && !auth.utilisateur) {
    await auth.chargerProfil();
  }
  return true;
});

export default router;

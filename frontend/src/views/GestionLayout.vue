<script setup>
/**
 * Ossature de l'interface de gestion desktop (maquette Maquettes_SHEQ_Desktop.html,
 * CDC 11.1 "deux interfaces, deux usages"). Barre latérale persistante +
 * zone de contenu (<router-view>) — remplace les boutons de navigation
 * ad hoc ajoutés route par route dans les premiers écrans desktop (EPI,
 * assistant documentaire, tableau de bord) : ne passait pas à l'échelle
 * au-delà de 3-4 modules.
 *
 * Seuls les modules ayant réellement un écran apparaissent, avec un lien —
 * même principe que MenuView.vue côté mobile. Les autres ne sont ajoutés que
 * lorsque leur écran existe, pas avant.
 *
 * Visibilité par permission réelle (2026-09-10, retour direct de
 * l'utilisateur — "les modules du sidebar ne s'affichent pas") : certains
 * liens (Tableau de bord, SLAM & permis, Formations, Satisfaction) restaient
 * visibles pour TOUS les rôles alors que leurs données sont réservées côté
 * serveur (CONSULTER_TABLEAU_BORD, GERER_FORMATIONS, TRAITER_SATISFACTION…) —
 * un technicien ou un collaborateur qui cliquait dessus tombait sur un écran
 * vide/en erreur (403), pas "un module qui ne s'affiche pas" au sens où on
 * le croirait absent, mais le symptôme observable était le même : rien ne
 * s'affiche. Chaque lien sensible porte désormais une clé `permission`
 * (celles de `app/core/permissions.py`, lues via `useRolesStore`) au lieu
 * d'une liste de rôles recopiée à la main — indérivable de ce que les
 * routes appliquent réellement, ça ne peut plus se désynchroniser.
 */
import { computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import Icone from "../components/Icone.vue";
import ModalPhotoProfil from "../components/ModalPhotoProfil.vue";
import NotificationsCloche from "../components/NotificationsCloche.vue";
import { useAvatar } from "../composables/useAvatar";
import { useAuthStore } from "../stores/auth";
import { LIBELLE_TYPE, routeDeResultat, useRechercheStore } from "../stores/recherche";
import { useRolesStore } from "../stores/roles";
import { THEMES, useThemeStore } from "../stores/theme";

const router = useRouter();
const route = useRoute();
const auth = useAuthStore();
const theme = useThemeStore();
const rolesStore = useRolesStore();

// Photo de profil (2026-09-10, retour direct de l'utilisateur — "insérer sa
// photo") : clic sur l'avatar du bloc profil pour l'ouvrir/la changer.
const photoOuverte = ref(false);
const { url: urlPhoto } = useAvatar(
  computed(() => auth.utilisateur?.id ?? null),
  computed(() => auth.utilisateur?.photo ?? null)
);
onMounted(() => rolesStore.charger());

// Recherche globale d'en-tête (revue d'ensemble 2026-09-10 — champ
// "Rechercher partout…" de la maquette). Débounce simple ; le clic sur un
// résultat ouvre l'écran concerné (les écrans desktop ont leur propre
// recherche interne pour affiner ensuite).
const recherche = useRechercheStore();
const termeRecherche = ref("");
let minuteur = null;
function surSaisieRecherche() {
  clearTimeout(minuteur);
  minuteur = setTimeout(() => recherche.lancer(termeRecherche.value), 250);
}
function ouvrirResultat(r) {
  const cible = routeDeResultat(r);
  recherche.fermer();
  termeRecherche.value = "";
  if (cible) router.push(cible);
}
// Fermeture différée : laisse le temps au @mousedown d'un résultat de partir
// avant que le menu ne disparaisse.
function fermerBientot() {
  setTimeout(() => recherche.fermer(), 150);
}

// Impression (2026-09-09, retour direct de l'utilisateur — "tous les
// documents renseignés doivent pouvoir être imprimés") : window.print()
// ouvre la boîte de dialogue d'impression du système, qui voit déjà toutes
// les imprimantes installées — une page web n'a ni besoin ni le droit de
// s'y connecter directement (limite du navigateur, pas de ce projet). La
// mise en page imprimée (masquage de la barre latérale et des contrôles,
// voir .no-print dans style.css) fait le reste du travail.
function imprimer() {
  window.print();
}

// Déconnexion volontaire (2026-09-10, retour direct de l'utilisateur —
// "on crée un module pour la déconnexion") : `auth.deconnecter()` existait
// déjà (utilisé automatiquement à l'expiration de session, voir main.js)
// mais n'était câblé à AUCUN bouton — impossible de se déconnecter soi-même
// sans vider le stockage du navigateur à la main. Pas de confirmation :
// l'action n'est pas destructrice (aucune donnée perdue, il suffit de se
// reconnecter).
function deconnecter() {
  auth.deconnecter();
  router.push({ name: "connexion" });
}

// Sections de la barre latérale repliables (2026-09-09, retour direct de
// l'utilisateur — "chaque titre doit être un dropdown"). Repli mémorisé
// (localStorage) pour survivre à un rechargement, mais jamais sur la
// section qui contient l'écran actif — sinon un rechargement de page
// pourrait faire disparaître le lien vers l'écran affiché.
const CLE_SECTIONS_REPLIEES = "sheq_sections_repliees";
function lireSectionsRepliees() {
  try {
    const brut = localStorage.getItem(CLE_SECTIONS_REPLIEES);
    return brut ? new Set(JSON.parse(brut)) : new Set();
  } catch {
    return new Set();
  }
}
const sectionsRepliees = ref(lireSectionsRepliees());

function sectionOuverte(section) {
  if (section.liens.some((l) => l.nom === route.name)) return true;
  return !sectionsRepliees.value.has(section.titre);
}

function basculerSection(titre) {
  const copie = new Set(sectionsRepliees.value);
  if (copie.has(titre)) copie.delete(titre);
  else copie.add(titre);
  sectionsRepliees.value = copie;
  try {
    localStorage.setItem(CLE_SECTIONS_REPLIEES, JSON.stringify([...copie]));
  } catch {
    // Stockage indisponible : le repli ne survit simplement pas au
    // rechargement, pas bloquant pour l'usage courant.
  }
}

const initiales = computed(() => {
  const u = auth.utilisateur;
  if (!u) return "";
  return `${u.prenom?.[0] ?? ""}${u.nom?.[0] ?? ""}`.toUpperCase();
});

// Un lien est visible si : ni `roles` ni `permission` (ouvert à tous) ; ou
// `roles` (liste figée, pour les cas qui ne se réduisent pas à une seule
// permission serveur, ex. Coffre-fort) ; ou `permission` (clé de
// `app/core/permissions.py`, résolue via useRolesStore — la clé inconnue
// est traitée comme "pas de restriction connue", jamais comme "masqué",
// pour qu'une faute de frappe ne fasse pas disparaître tout un module).
function lienVisible(lien) {
  if (lien.roles) return lien.roles.includes(auth.utilisateur?.role);
  if (lien.permission) {
    const roles = rolesStore.rolesPour(lien.permission);
    return roles === null || roles.includes(auth.utilisateur?.role);
  }
  return true;
}

const sectionsVisibles = computed(() =>
  SECTIONS.filter((section) => !section.roles || section.roles.includes(auth.utilisateur?.role))
    .map((section) => ({
      ...section,
      liens: section.liens.filter(lienVisible),
    }))
    .filter((section) => section.liens.length)
);

const SECTIONS = [
  {
    titre: "PILOTAGE",
    liens: [
      // Vue d'ensemble tous services confondus (accidents, signalements de
      // tout le personnel...) — réservée aux rôles de pilotage côté serveur
      // (CONSULTER_TABLEAU_BORD) ; le menu mobile appliquait déjà cette
      // restriction (MenuView.vue, `peutVoirTableauBord`), pas la barre
      // latérale desktop jusqu'ici.
      { nom: "gestion-tableau-de-bord", icone: "home", libelle: "Tableau de bord", permission: "CONSULTER_TABLEAU_BORD" },
      { nom: "gestion-risques", icone: "target", libelle: "Risques" },
      { nom: "gestion-actions", icone: "check", libelle: "Plan d'action" },
    ],
  },
  {
    titre: "TERRAIN",
    liens: [
      { nom: "signalements", icone: "alert", libelle: "Signalements" },
      // Vue pilotage : TOUTES les évaluations SLAM et TOUS les permis
      // (validation comprise), pas la saisie d'un technicien pour lui-même
      // (mobile, SlamView/PermisView, non concernées). Réservée côté serveur
      // (GET /slam exige CONSULTER_TABLEAU_BORD).
      { nom: "gestion-permis", icone: "climb", libelle: "SLAM & permis", permission: "CONSULTER_TABLEAU_BORD" },
      { nom: "gestion-epi", icone: "vest", libelle: "EPI" },
      { nom: "gestion-inspections", icone: "clip", libelle: "Inspections" },
      { nom: "gestion-parc", icone: "antenna", libelle: "Parc & configs" },
      // Section 5.2.4 du CDC : "l'accès au coffre-fort n'est pas accordé par
      // défaut au référent SHEQ, dont la fonction ne le justifie pas" — lien
      // masqué pour ce rôle plutôt que montré puis vide (le référent SHEQ
      // n'a accès à AUCUN secret, quel que soit son role_requis). Pas une
      // permission unique côté serveur (dépend du role_requis par secret) :
      // liste de rôles conservée telle quelle, pas de clé `permission`.
      { nom: "gestion-coffre-fort", icone: "key", libelle: "Coffre-fort", roles: ["technicien", "responsable", "administrateur"] },
    ],
  },
  {
    titre: "SYSTÈME",
    liens: [
      // Vérifié en conditions réelles (2026-09-10) : contrairement à une
      // première hypothèse, GET /formations/competences est ouvert à tous
      // (seule sa CRÉATION est réservée) ; seul /matrice est restreint
      // (ROLES_VUE_ENSEMBLE), et FormationsDesktopView l'appelle déjà dans
      // son propre try/catch dédié (matrice vide affichée, pas d'erreur
      // bloquante) — l'écran fonctionne pour tous les rôles. Pas de
      // permission gating ici, comme sur mobile.
      { nom: "gestion-formations", icone: "cap", libelle: "Formations" },
      { nom: "gestion-audits", icone: "list", libelle: "Audits & revues" },
      { nom: "gestion-documents", icone: "doc", libelle: "Documents" },
      { nom: "gestion-visiteurs", icone: "door", libelle: "Visiteurs" },
      { nom: "gestion-dechets", icone: "recycle", libelle: "Déchets" },
      // Liste des enquêtes et réponses — réservée côté serveur
      // (TRAITER_SATISFACTION). L'ENVOI d'une enquête, lui, reste ouvert au
      // technicien (ENVOYER_ENQUETE_SATISFACTION, distinct) : pas concerné,
      // il n'a pas d'écran dédié dans ce menu.
      { nom: "gestion-satisfaction", icone: "star", libelle: "Satisfaction", permission: "TRAITER_SATISFACTION" },
      { nom: "gestion-assistant-documentaire", icone: "chat", libelle: "Assistant documentaire" },
    ],
  },
  {
    titre: "ADMINISTRATION",
    // Restriction de section conservée en plus des permissions par lien (pas
    // redondant : évite de calculer 3 permissions pour rien quand la section
    // entière doit disparaître).
    roles: ["administrateur"],
    liens: [
      { nom: "gestion-utilisateurs", icone: "users", libelle: "Utilisateurs & rôles", permission: "GERER_UTILISATEURS" },
      { nom: "gestion-sites", icone: "door", libelle: "Sites", permission: "GERER_SITES" },
      { nom: "gestion-parametres", icone: "cog", libelle: "Paramètres", permission: "GERER_UTILISATEURS" },
    ],
  },
];
</script>

<template>
  <div class="gestion-shell">
    <aside class="side no-print">
      <div class="top">
        <div class="mk"><Icone nom="hirondelle" taille="lg" /></div>
        <div><b>SHEQ Management</b><span>Hirondelles IT Lab</span></div>
      </div>
      <!-- Attend que le chargement des permissions réelles ait ABOUTI (succès
           OU échec) avant d'afficher les liens sensibles (Tableau de bord,
           SLAM & permis, Formations, Satisfaction…) : sans cette attente, ils
           apparaîtraient un instant pour tout le monde puis disparaîtraient
           pour les rôles non habilités — un clignotement trompeur plutôt
           qu'une vraie correction. Chargement quasi instantané en local, pas
           de squelette visible en pratique. En cas d'échec du chargement
           (API indisponible), `rolesPour()` renvoie null pour toute clé et
           `lienVisible()` retombe sur "pas de restriction connue" : la barre
           latérale reste utilisable plutôt que de rester vide indéfiniment. -->
      <template v-if="rolesStore.donnees || rolesStore.erreur">
        <template v-for="section in sectionsVisibles" :key="section.titre">
          <button
            class="navsec"
            :aria-expanded="sectionOuverte(section)"
            @click="basculerSection(section.titre)"
          >
            {{ section.titre }}
            <Icone nom="chev" taille="sm" class="navsec-chev" :class="{ ouverte: sectionOuverte(section) }" />
          </button>
          <template v-if="sectionOuverte(section)">
            <button
              v-for="lien in section.liens"
              :key="lien.nom"
              class="nv"
              :class="{ on: route.name === lien.nom }"
              @click="router.push({ name: lien.nom })"
            >
              <Icone :nom="lien.icone" />{{ lien.libelle }}
            </button>
          </template>
        </template>
      </template>
      <div class="user">
        <button class="av" type="button" aria-label="Ma photo de profil" title="Ma photo de profil" @click="photoOuverte = true">
          <img v-if="urlPhoto" :src="urlPhoto" alt="" />
          <template v-else>{{ initiales }}</template>
        </button>
        <div>
          <b>{{ auth.utilisateur ? `${auth.utilisateur.prenom} ${auth.utilisateur.nom}` : "" }}</b>
          <span>{{ auth.utilisateur?.role?.replace("_", " ") }}</span>
        </div>
        <button class="deco" type="button" aria-label="Se déconnecter" title="Se déconnecter" @click="deconnecter">
          <Icone nom="logout" taille="sm" />
        </button>
      </div>
    </aside>

    <ModalPhotoProfil v-if="photoOuverte" @fermer="photoOuverte = false" />
    <div class="gestion-main">
      <header class="gestion-top">
        <h1>{{ route.meta.titre ?? "" }}</h1>
        <div class="no-print srch" style="margin-left: 24px; position: relative" @keydown.escape="recherche.fermer()">
          <Icone nom="search" taille="sm" />
          <input
            v-model="termeRecherche"
            placeholder="Rechercher partout…"
            aria-label="Recherche globale"
            @input="surSaisieRecherche"
            @focus="termeRecherche.length >= 2 && (recherche.ouvert = true)"
            @blur="fermerBientot"
          />
          <div
            v-if="recherche.ouvert && (recherche.resultats.length || !recherche.chargement)"
            class="recherche-menu"
          >
            <p v-if="!recherche.resultats.length" class="recherche-vide">Aucun résultat</p>
            <button
              v-for="r in recherche.resultats"
              :key="`${r.type}-${r.id}`"
              type="button"
              class="recherche-item"
              @mousedown.prevent="ouvrirResultat(r)"
            >
              <span class="tag t-gy">{{ LIBELLE_TYPE[r.type] }}</span>
              <span class="recherche-item-tx">
                <b>{{ r.libelle }}</b>
                <span v-if="r.sous_libelle && r.sous_libelle !== r.libelle">{{ r.sous_libelle }}</span>
              </span>
            </button>
          </div>
        </div>
        <div class="no-print" style="margin-left: auto; display: flex; align-items: center; gap: 10px">
          <select
            class="inp"
            style="width: auto; padding: 6px 10px; font-size: 12px"
            :value="theme.theme"
            aria-label="Thème"
            @change="theme.appliquer($event.target.value)"
          >
            <option v-for="t in THEMES" :key="t.valeur" :value="t.valeur">{{ t.libelle }}</option>
          </select>
          <button class="btn gh sm" style="width: auto" @click="imprimer">
            <Icone nom="print" taille="sm" />Imprimer
          </button>
          <NotificationsCloche />
        </div>
      </header>
      <div class="gestion-view">
        <router-view />
      </div>
    </div>
  </div>
</template>

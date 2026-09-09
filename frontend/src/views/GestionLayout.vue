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
 */
import { computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import Icone from "../components/Icone.vue";
import NotificationsCloche from "../components/NotificationsCloche.vue";
import { useAuthStore } from "../stores/auth";

const router = useRouter();
const route = useRoute();
const auth = useAuthStore();

const initiales = computed(() => {
  const u = auth.utilisateur;
  if (!u) return "";
  return `${u.prenom?.[0] ?? ""}${u.nom?.[0] ?? ""}`.toUpperCase();
});

const sectionsVisibles = computed(() =>
  SECTIONS.filter((section) => !section.roles || section.roles.includes(auth.utilisateur?.role))
    .map((section) => ({
      ...section,
      liens: section.liens.filter((lien) => !lien.roles || lien.roles.includes(auth.utilisateur?.role)),
    }))
    .filter((section) => section.liens.length)
);

const SECTIONS = [
  {
    titre: "PILOTAGE",
    liens: [
      { nom: "gestion-tableau-de-bord", icone: "home", libelle: "Tableau de bord" },
      { nom: "gestion-risques", icone: "target", libelle: "Risques" },
      { nom: "gestion-actions", icone: "check", libelle: "Plan d'action" },
    ],
  },
  {
    titre: "TERRAIN",
    liens: [
      { nom: "signalements", icone: "alert", libelle: "Signalements" },
      { nom: "gestion-permis", icone: "climb", libelle: "SLAM & permis" },
      { nom: "gestion-epi", icone: "vest", libelle: "EPI" },
      { nom: "gestion-inspections", icone: "clip", libelle: "Inspections" },
      { nom: "gestion-parc", icone: "antenna", libelle: "Parc & configs" },
      // Section 5.2.4 du CDC : "l'accès au coffre-fort n'est pas accordé par
      // défaut au référent SHEQ, dont la fonction ne le justifie pas" — lien
      // masqué pour ce rôle plutôt que montré puis vide (le référent SHEQ
      // n'a accès à AUCUN secret, quel que soit son role_requis).
      { nom: "gestion-coffre-fort", icone: "key", libelle: "Coffre-fort", roles: ["technicien", "responsable", "administrateur"] },
    ],
  },
  {
    titre: "SYSTÈME",
    liens: [
      { nom: "gestion-formations", icone: "cap", libelle: "Formations" },
      { nom: "gestion-audits", icone: "list", libelle: "Audits & revues" },
      { nom: "gestion-documents", icone: "doc", libelle: "Documents" },
      { nom: "gestion-visiteurs", icone: "door", libelle: "Visiteurs" },
      { nom: "gestion-dechets", icone: "recycle", libelle: "Déchets" },
      { nom: "gestion-satisfaction", icone: "star", libelle: "Satisfaction" },
      { nom: "gestion-assistant-documentaire", icone: "chat", libelle: "Assistant documentaire" },
    ],
  },
  {
    titre: "ADMINISTRATION",
    // Seule section restreinte par rôle : `GERER_UTILISATEURS` (backend) n'ouvre
    // cette route qu'à l'administrateur — masquer le lien pour les autres
    // rôles évite un aller-retour pour un 403 prévisible.
    roles: ["administrateur"],
    liens: [{ nom: "gestion-utilisateurs", icone: "users", libelle: "Utilisateurs & rôles" }],
  },
];
</script>

<template>
  <div class="gestion-shell">
    <aside class="side">
      <div class="top">
        <div class="mk">H</div>
        <div><b>SHEQ Management</b><span>Hirondelles IT Lab</span></div>
      </div>
      <template v-for="section in sectionsVisibles" :key="section.titre">
        <div class="navsec">{{ section.titre }}</div>
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
      <div class="user">
        <div class="av">{{ initiales }}</div>
        <div>
          <b>{{ auth.utilisateur ? `${auth.utilisateur.prenom} ${auth.utilisateur.nom}` : "" }}</b>
          <span>{{ auth.utilisateur?.role?.replace("_", " ") }}</span>
        </div>
      </div>
    </aside>
    <div class="gestion-main">
      <header class="gestion-top">
        <h1>{{ route.meta.titre ?? "" }}</h1>
        <div style="margin-left: auto"><NotificationsCloche /></div>
      </header>
      <div class="gestion-view">
        <router-view />
      </div>
    </div>
  </div>
</template>

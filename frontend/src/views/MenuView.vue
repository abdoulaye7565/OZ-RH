<script setup>
/**
 * Menu des modules — vue mobile (maquette #s-menu).
 *
 * Écart assumé, à mettre à jour au fil des prompts suivants : la maquette
 * réelle liste 14 modules groupés en 3 catégories ; seuls ceux qui ont
 * effectivement un écran apparaissent ici (même principe que
 * SignalementsView.vue : "mieux vaut les omettre que proposer des boutons
 * qui ne mènent nulle part").
 */
import { computed, ref } from "vue";
import { useRouter } from "vue-router";
import Icone from "../components/Icone.vue";
import ModalPhotoProfil from "../components/ModalPhotoProfil.vue";
import BandeauReseau from "../components/BandeauReseau.vue";
import { useAvatar } from "../composables/useAvatar";
import { useAuthStore } from "../stores/auth";
import { THEMES, useThemeStore } from "../stores/theme";

const router = useRouter();
const auth = useAuthStore();
const theme = useThemeStore();

// Déconnexion volontaire (2026-09-10, retour direct de l'utilisateur — "on
// crée un module pour la déconnexion") : `auth.deconnecter()` existait déjà
// (utilisé automatiquement à l'expiration de session, main.js) mais n'était
// câblé à aucun bouton, desktop ou mobile. Pas de confirmation : action non
// destructrice.
function deconnecter() {
  auth.deconnecter();
  router.push({ name: "connexion" });
}

// Photo de profil (2026-09-10, retour direct de l'utilisateur — "insérer sa
// photo") — même modale que côté desktop (GestionLayout.vue).
const photoOuverte = ref(false);
const { url: urlPhoto } = useAvatar(
  computed(() => auth.utilisateur?.id ?? null),
  computed(() => auth.utilisateur?.photo ?? null)
);
const initiales = computed(() => {
  const u = auth.utilisateur;
  if (!u) return "";
  return `${u.prenom?.[0] ?? ""}${u.nom?.[0] ?? ""}`.toUpperCase();
});

const peutVoirTableauBord = computed(() =>
  ["administrateur", "referent_sheq", "responsable"].includes(auth.utilisateur?.role)
);
// Section 5.2.4 du CDC : le référent SHEQ n'a jamais accès au coffre-fort,
// quel que soit le rôle minimal requis par un secret donné.
const peutVoirCoffreFort = computed(() => ["technicien", "responsable", "administrateur"].includes(auth.utilisateur?.role));
</script>

<template>
  <div class="ecran-mobile">
    <BandeauReseau />
    <header class="hd">
      <button class="back" aria-label="Retour" @click="router.push({ name: 'signalements' })"><Icone nom="back" /></button>
      <div>
        <h1>Modules</h1>
        <div class="sub">Selon votre rôle : {{ auth.utilisateur?.role?.replace("_", " ") }}</div>
      </div>
    </header>

    <div class="wrap">
      <div class="body">
        <div class="pad">
          <div class="sec">PRÉVENTION</div>
          <div class="modgrid" style="margin-bottom: 14px">
            <button class="qa" @click="router.push({ name: 'risques' })">
              <span class="ic" style="background: var(--red-soft); color: var(--red)"><Icone nom="target" /></span>
              <span><b>Risques</b><span>Registre</span></span>
            </button>
            <button class="qa" @click="router.push({ name: 'epi' })">
              <span class="ic" style="background: var(--orange-soft); color: var(--orange)"><Icone nom="vest" /></span>
              <span><b>EPI antichute</b><span>Vérifications</span></span>
            </button>
            <button class="qa" @click="router.push({ name: 'signalements' })">
              <span class="ic" style="background: var(--red-soft); color: var(--red)"><Icone nom="alert" /></span>
              <span><b>Signalements</b><span>Terrain</span></span>
            </button>
            <button class="qa" @click="router.push({ name: 'actions' })">
              <span class="ic" style="background: var(--green-soft); color: var(--green)"><Icone nom="check" /></span>
              <span><b>Plan d'action</b><span>Suivi</span></span>
            </button>
          </div>

          <div class="sec">TERRAIN</div>
          <div class="modgrid" style="margin-bottom: 14px">
            <button class="qa" @click="router.push({ name: 'slam' })">
              <span class="ic" style="background: var(--gold-soft); color: var(--gold)"><Icone nom="climb" /></span>
              <span><b>SLAM</b><span>Avant chaque montée</span></span>
            </button>
            <button class="qa" @click="router.push({ name: 'permis-liste' })">
              <span class="ic" style="background: var(--navy-soft); color: var(--navy2)"><Icone nom="clip" /></span>
              <span><b>Permis</b><span>Demande &amp; suivi</span></span>
            </button>
            <button class="qa" @click="router.push({ name: 'parc' })">
              <span class="ic" style="background: var(--navy-soft); color: var(--navy2)"><Icone nom="antenna" /></span>
              <span><b>Parc &amp; configs</b><span>Équipements</span></span>
            </button>
            <button class="qa" @click="router.push({ name: 'inspections' })">
              <span class="ic" style="background: var(--navy-soft); color: var(--navy2)"><Icone nom="clip" /></span>
              <span><b>Inspections</b><span>Checklists terrain</span></span>
            </button>
            <button v-if="peutVoirCoffreFort" class="qa" @click="router.push({ name: 'coffre-fort' })">
              <span class="ic" style="background: var(--navy-soft); color: var(--navy2)"><Icone nom="key" /></span>
              <span><b>Coffre-fort</b><span>Identifiants chiffrés</span></span>
            </button>
          </div>

          <div class="sec">PILOTAGE</div>
          <div class="modgrid">
            <button v-if="peutVoirTableauBord" class="qa" @click="router.push({ name: 'tableau-de-bord' })">
              <span class="ic" style="background: var(--blue-soft); color: var(--blue)"><Icone nom="chart" /></span>
              <span><b>Tableau de bord</b><span>Vue d'ensemble</span></span>
            </button>
            <button class="qa" @click="router.push({ name: 'formations' })">
              <span class="ic" style="background: var(--blue-soft); color: var(--blue)"><Icone nom="cap" /></span>
              <span><b>Formations</b><span>Compétences · quiz</span></span>
            </button>
            <button class="qa" @click="router.push({ name: 'audits' })">
              <span class="ic" style="background: var(--blue-soft); color: var(--blue)"><Icone nom="list" /></span>
              <span><b>Audits &amp; revues</b><span>Auto-diagnostic</span></span>
            </button>
            <button class="qa" @click="router.push({ name: 'documents' })">
              <span class="ic" style="background: var(--gold-soft); color: var(--gold)"><Icone nom="doc" /></span>
              <span><b>Documents</b><span>Système documentaire</span></span>
            </button>
            <button class="qa" @click="router.push({ name: 'visiteurs' })">
              <span class="ic" style="background: #f1f3f7; color: var(--mut)"><Icone nom="door" /></span>
              <span><b>Visiteurs</b><span>Accueil</span></span>
            </button>
            <button class="qa" @click="router.push({ name: 'dechets' })">
              <span class="ic" style="background: var(--green-soft); color: var(--green)"><Icone nom="recycle" /></span>
              <span><b>Déchets</b><span>Registre DEEE</span></span>
            </button>
            <button class="qa" @click="router.push({ name: 'assistant-documentaire' })">
              <span class="ic" style="background: var(--gold-soft); color: var(--gold)"><Icone nom="chat" /></span>
              <span><b>Assistant documentaire</b><span>Questions au SMI</span></span>
            </button>
          </div>

          <div class="sec" style="margin-top: 14px">APPARENCE</div>
          <div class="card">
            <div class="cb">
              <label class="f" for="menu-theme">Thème</label>
              <select
                id="menu-theme"
                class="inp"
                :value="theme.theme"
                @change="theme.appliquer($event.target.value)"
              >
                <option v-for="t in THEMES" :key="t.valeur" :value="t.valeur">{{ t.libelle }}</option>
              </select>
            </div>
          </div>

          <div class="banner info" style="margin-top: 14px">
            <div>
              La satisfaction client et la gestion des utilisateurs se
              pilotent depuis l'interface de gestion (desktop, réservée aux
              rôles habilités) — le questionnaire de satisfaction, lui, est
              envoyé par lien direct au client, sans passer par ce menu.
            </div>
          </div>

          <div class="sec" style="margin-top: 14px">COMPTE</div>
          <div class="card" style="padding: 12px; margin-top: 4px">
            <div style="display: flex; align-items: center; gap: 10px">
              <button class="av" type="button" style="width: 44px; height: 44px; font-size: 15px" aria-label="Ma photo de profil" @click="photoOuverte = true">
                <img v-if="urlPhoto" :src="urlPhoto" alt="" />
                <template v-else>{{ initiales }}</template>
              </button>
              <div style="flex: 1; min-width: 0">
                <b style="display: block; font-size: 13px">{{ auth.utilisateur ? `${auth.utilisateur.prenom} ${auth.utilisateur.nom}` : "" }}</b>
                <span style="font-size: 11px; color: var(--mut)">{{ auth.utilisateur?.role?.replace("_", " ") }}</span>
              </div>
            </div>
            <button class="btn gh sm" style="width: 100%; margin-top: 10px" @click="photoOuverte = true">
              <Icone nom="cam" taille="sm" />Ma photo de profil
            </button>
          </div>
          <button class="btn gh" style="margin-top: 8px" @click="deconnecter">
            <Icone nom="logout" taille="sm" />Se déconnecter
          </button>

          <div style="height: 20px"></div>
        </div>
      </div>
    </div>

    <nav class="tabs">
      <button class="tb" @click="router.push({ name: 'accueil' })"><Icone nom="home" />Accueil</button>
      <button class="tb" @click="router.push({ name: 'signalements' })"><Icone nom="alert" />Signaux</button>
      <button class="tb" @click="router.push({ name: 'slam' })"><Icone nom="climb" />SLAM</button>
      <button class="tb" @click="router.push({ name: 'tableau-de-bord' })"><Icone nom="chart" />Tableau</button>
      <button class="tb" @click="router.push({ name: 'assistant-documentaire' })"><Icone nom="chat" />Assistant</button>
      <button class="tb on"><Icone nom="grid" />Menu</button>
    </nav>

    <ModalPhotoProfil v-if="photoOuverte" @fermer="photoOuverte = false" />
  </div>
</template>

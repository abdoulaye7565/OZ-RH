<script setup>
/**
 * Contenu d'un dossier du SMI — vue mobile. Reprend le rendu par ligne de
 * l'ancien écran Documents (unique jusqu'ici), désormais filtré par dossier
 * (voir DocumentsView.vue pour l'écran de dossiers et la justification).
 */
import { computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import Icone from "../components/Icone.vue";
import BandeauReseau from "../components/BandeauReseau.vue";
import { useAuthStore } from "../stores/auth";
import { useDocumentsStore } from "../stores/documents";
import { DOSSIERS, dossierDe } from "../utils/dossiersDocuments";
import api from "../services/api";

const route = useRoute();
const router = useRouter();
const auth = useAuthStore();
const documents = useDocumentsStore();
onMounted(() => documents.charger());

const dossier = computed(() => DOSSIERS.find((d) => d.cle === route.params.dossier));
const listeDossier = computed(() => documents.liste.filter((d) => dossierDe(d) === route.params.dossier));

const peutGerer = computed(() => ["referent_sheq", "administrateur"].includes(auth.utilisateur?.role));
const peutApprouver = computed(() => ["responsable", "administrateur"].includes(auth.utilisateur?.role));

const STYLE_STATUT = {
  brouillon: { tag: "t-gy", libelle: "BROUILLON" },
  en_approbation: { tag: "t-gd", libelle: "APPROBATION" },
  en_vigueur: { tag: "t-gr", libelle: "EN VIGUEUR" },
  archive: { tag: "t-gy", libelle: "ARCHIVE" },
};

async function ouvrirFichier(id) {
  try {
    const reponse = await api.requete(`/api/v1/documents/${id}/fichier`, { brut: true });
    const blob = await reponse.blob();
    window.open(URL.createObjectURL(blob), "_blank");
  } catch {
    // Aucun fichier joint, ou droits insuffisants : rien ne s'ouvre.
  }
}
</script>

<template>
  <div class="ecran-mobile">
    <BandeauReseau />
    <header class="hd">
      <button class="back" aria-label="Retour" @click="router.push({ name: 'documents' })"><Icone nom="back" /></button>
      <div>
        <h1>{{ dossier?.nom ?? "Dossier" }}</h1>
        <div class="sub">{{ listeDossier.length }} document{{ listeDossier.length > 1 ? "s" : "" }}</div>
      </div>
    </header>

    <div class="wrap">
      <div class="body">
        <div class="pad">
          <div v-if="documents.erreur" class="banner err">{{ documents.erreur }}</div>

          <div class="banner info" style="margin-bottom: 11px">
            <Icone nom="doc" taille="sm" style="margin-top: 1px" />
            <div>{{ dossier?.description }}</div>
          </div>

          <div v-for="d in listeDossier" :key="d.id" class="row">
            <span class="lead" :class="d.statut === 'en_vigueur' ? 'gr' : d.statut === 'en_approbation' ? 'gd' : 'gy'"><Icone nom="doc" /></span>
            <div class="tx">
              <b>{{ d.reference }} · {{ d.intitule }}</b>
              <div class="meta">
                <span>v{{ d.version }}</span>
                <span>{{ d.accuses_lecture.length }} lecture{{ d.accuses_lecture.length > 1 ? "s" : "" }}</span>
              </div>
              <div class="meta" style="margin-top: 5px">
                <button v-if="d.statut === 'brouillon' && peutGerer" class="tag t-gd" style="border: 0; cursor: pointer" @click="documents.soumettreApprobation(d.id)">Soumettre</button>
                <button v-if="d.statut === 'en_approbation' && peutApprouver" class="tag t-gr" style="border: 0; cursor: pointer" @click="documents.approuver(d.id)">Approuver</button>
                <button v-if="d.statut === 'en_vigueur'" class="tag t-bl" style="border: 0; cursor: pointer" @click="documents.accuserLecture(d.id)">Accuser lecture</button>
                <button v-if="d.fichier" class="tag t-gy" style="border: 0; cursor: pointer" @click="ouvrirFichier(d.id)">Ouvrir le fichier</button>
              </div>
            </div>
            <span class="tag" :class="STYLE_STATUT[d.statut].tag">{{ STYLE_STATUT[d.statut].libelle }}</span>
          </div>

          <div v-if="!documents.chargement && !listeDossier.length" class="empty">
            <div class="ic"><Icone nom="doc" taille="lg" /></div>
            <b>Dossier vide</b>
          </div>

          <div style="height: 56px"></div>
        </div>
      </div>
    </div>

    <nav class="tabs">
      <button class="tb" @click="router.push({ name: 'accueil' })"><Icone nom="home" />Accueil</button>
      <button class="tb" @click="router.push({ name: 'signalements' })"><Icone nom="alert" />Signaux</button>
      <button class="tb" @click="router.push({ name: 'slam' })"><Icone nom="climb" />SLAM</button>
      <button class="tb" @click="router.push({ name: 'tableau-de-bord' })"><Icone nom="chart" />Tableau</button>
      <button class="tb" @click="router.push({ name: 'menu' })"><Icone nom="grid" />Menu</button>
    </nav>
  </div>
</template>

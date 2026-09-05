<script setup>
/**
 * Écran "Liste des signalements" — maquette, section #s-siglist (figure A.4 du CDC).
 *
 * Écart assumé : la barre d'onglets du bas (Accueil/Signaux/SLAM/Parc/Tableau)
 * de la maquette n'est reprise qu'avec les deux destinations qui existent
 * réellement — les trois autres (SLAM, Parc, Tableau de bord) n'ont pas encore
 * d'écran (lots 2, 3 et 1.5) : mieux vaut les omettre que proposer des boutons
 * qui ne mènent nulle part.
 */
import { computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import Icone from "../components/Icone.vue";
import BandeauReseau from "../components/BandeauReseau.vue";
import { FILTRES_STATUT, useSignalementsStore } from "../stores/signalements";

const router = useRouter();
const signalements = useSignalementsStore();

onMounted(() => signalements.charger());

const total = computed(() => signalements.liste.length);

function libelleFiltre(filtre) {
  if (filtre.valeur === null) return `${filtre.libelle} · ${total.value}`;
  return `${filtre.libelle} · ${signalements.nombreParStatut[filtre.valeur] ?? 0}`;
}

const STYLE_STATUT = {
  nouveau: { lead: "red", tag: "t-red", icone: "alert", libelle: "NOUVEAU" },
  en_analyse: { lead: "gd", tag: "t-gd", icone: "search", libelle: "EN ANALYSE" },
  actions_definies: { lead: "bl", tag: "t-bl", icone: "alert", libelle: "ACTIONS DÉFINIES" },
  cloture: { lead: "gr", tag: "t-gr", icone: "check", libelle: "CLÔTURÉ" },
};

function styleDe(statut) {
  return STYLE_STATUT[statut] ?? STYLE_STATUT.nouveau;
}

function formaterDate(iso) {
  return new Date(iso).toLocaleDateString("fr-FR", { day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit" });
}
</script>

<template>
  <div class="ecran-mobile">
    <BandeauReseau />
    <header class="hd">
      <div class="mk">H</div>
      <div>
        <h1>Signalements</h1>
        <div class="sub">{{ total }} signalement{{ total > 1 ? "s" : "" }}</div>
      </div>
    </header>

    <div class="wrap">
      <div class="body">
        <div class="pad">
          <div class="segs" style="margin-bottom: 12px">
            <button
              v-for="filtre in FILTRES_STATUT"
              :key="filtre.valeur ?? 'tous'"
              type="button"
              class="seg"
              :class="{ on: signalements.filtreStatut === filtre.valeur }"
              @click="signalements.definirFiltre(filtre.valeur)"
            >
              {{ libelleFiltre(filtre) }}
            </button>
          </div>

          <div v-if="signalements.erreur" class="banner err">{{ signalements.erreur }}</div>

          <div v-if="signalements.chargement" class="skel" style="height: 64px"></div>

          <div v-else-if="!signalements.liste.length" class="empty">
            <div class="ic"><Icone nom="alert" taille="lg" /></div>
            <b>Aucun signalement</b>
            <p>Créez le premier signalement avec le bouton ci-dessous.</p>
          </div>

          <div v-for="s in signalements.liste" :key="s.id" class="row">
            <span class="lead" :class="styleDe(s.statut).lead">
              <Icone :nom="styleDe(s.statut).icone" />
            </span>
            <div class="tx">
              <b>{{ s.lieu }}</b>
              <div class="meta">
                <span>{{ s.reference ?? "en attente de référence" }}</span>
                <span>{{ formaterDate(s.date_saisie) }}</span>
                <span>{{ s.anonyme ? "Anonyme" : `Utilisateur #${s.auteur_id}` }}</span>
                <span v-if="s.photos?.length">{{ s.photos.length }} photo{{ s.photos.length > 1 ? "s" : "" }}</span>
              </div>
            </div>
            <span class="tag" :class="styleDe(s.statut).tag">{{ styleDe(s.statut).libelle }}</span>
          </div>

          <div style="height: 56px"></div>
        </div>
      </div>
      <button class="fab" aria-label="Nouveau signalement" @click="router.push({ name: 'nouveau-signalement' })">
        <Icone nom="plus" taille="lg" />
      </button>
    </div>

    <nav class="tabs">
      <button class="tb" @click="router.push({ name: 'accueil' })"><Icone nom="home" />Accueil</button>
      <button class="tb on"><Icone nom="alert" />Signaux</button>
      <button class="tb" @click="router.push({ name: 'tableau-de-bord' })"><Icone nom="chart" />Tableau</button>
    </nav>
  </div>
</template>

<script setup>
/**
 * Tableau de bord — vue mobile simplifiée (maquette #s-tdb, figure A.10 du CDC).
 *
 * Mis à jour le 2026-09-08 (synchronisation aux données réelles) : les 4
 * tuiles reprennent maintenant celles de la maquette (accidents,
 * signalements, EPI à vérifier, conformité inspections) — EPI et
 * Inspections existent depuis le chantier du 2026-09-07 et alimentent des
 * indicateurs réels côté API (`tableau_bord_service.py`). Seul l'écart
 * "avec arrêt" reste assumé : aucun champ ne distingue un accident avec
 * arrêt de travail d'un accident sans arrêt dans le dictionnaire de données
 * du signalement — la tuile montre les accidents enregistrés, sans cette
 * distinction non modélisée.
 */
import { computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import Icone from "../components/Icone.vue";
import BandeauReseau from "../components/BandeauReseau.vue";
import { useTableauBordStore } from "../stores/tableauBord";

const router = useRouter();
const tdb = useTableauBordStore();

onMounted(() => tdb.charger());

const MOIS = ["Jan", "Fév", "Mar", "Avr", "Mai", "Juin", "Juil", "Août", "Sep", "Oct", "Nov", "Déc"];

const histogramme = computed(() => {
  const points = tdb.donnees?.signalements?.par_mois ?? [];
  return points.slice(-4);
});

const maxHistogramme = computed(() => Math.max(1, ...histogramme.value.map((p) => p.nombre)));

const plan = computed(() => {
  const a = tdb.donnees?.actions;
  if (!a) return null;
  const total = Object.values(a.par_statut).reduce((s, n) => s + n, 0);
  return { ...a, total };
});

function pourcent(n, total) {
  return total ? Math.round((n / total) * 100) : 0;
}

const epiAVerifier = computed(() => {
  const e = tdb.donnees?.epi;
  return e ? e.a_verifier_bientot + e.verifications_depassees : 0;
});
const conformiteInspections = computed(() => {
  const taux = tdb.donnees?.inspections?.taux_conformite_moyen;
  return taux === null || taux === undefined ? null : Math.round(taux * 100);
});
</script>

<template>
  <div class="ecran-mobile">
    <BandeauReseau />
    <header class="hd">
      <div class="mk"><Icone nom="hirondelle" taille="lg" /></div>
      <div>
        <h1>Tableau de bord</h1>
        <div class="sub">Vue d'ensemble de la prévention</div>
      </div>
    </header>

    <div class="wrap">
      <div class="body">
        <div class="pad">
          <div v-if="tdb.erreur" class="banner err">{{ tdb.erreur }}</div>
          <div v-else-if="tdb.chargement" class="skel" style="height: 80px"></div>

          <template v-else-if="tdb.donnees">
            <div class="metrics four">
              <div class="met" :class="tdb.donnees.securite.accidents_periode > 0 ? 'd' : 'g'">
                <div class="v">{{ tdb.donnees.securite.accidents_periode }}</div><div class="l">accidents</div>
              </div>
              <div class="met"><div class="v">{{ tdb.donnees.signalements.total_periode }}</div><div class="l">signalements</div></div>
              <div class="met" :class="epiAVerifier > 0 ? 'a' : 'g'">
                <div class="v">{{ epiAVerifier }}</div><div class="l">EPI à vérifier</div>
              </div>
              <div class="met" :class="conformiteInspections !== null && conformiteInspections < 90 ? 'a' : 'g'">
                <div class="v">{{ conformiteInspections !== null ? `${conformiteInspections}%` : "—" }}</div><div class="l">conformité</div>
              </div>
            </div>

            <div style="height: 14px"></div>

            <div v-if="plan" class="card" style="padding: 13px">
              <div class="sec" style="margin-bottom: 11px">
                PLAN D'ACTION <span class="n">{{ plan.total }} actions</span>
              </div>
              <div class="bar">
                <div class="lb"><b>Réalisées</b><span>{{ plan.par_statut.cloturee }}</span></div>
                <div class="trk"><div class="fl g" :style="{ width: pourcent(plan.par_statut.cloturee, plan.total) + '%' }"></div></div>
              </div>
              <div class="bar">
                <div class="lb"><b>En cours</b><span>{{ plan.par_statut.en_cours }}</span></div>
                <div class="trk"><div class="fl gd" :style="{ width: pourcent(plan.par_statut.en_cours, plan.total) + '%' }"></div></div>
              </div>
              <div class="bar" style="margin-bottom: 0">
                <div class="lb"><b>Ouvertes</b><span>{{ plan.par_statut.ouverte }}</span></div>
                <div class="trk"><div class="fl n" :style="{ width: pourcent(plan.par_statut.ouverte, plan.total) + '%' }"></div></div>
              </div>
            </div>

            <div style="height: 10px"></div>

            <div class="card" style="padding: 13px">
              <div class="sec" style="margin-bottom: 11px">SIGNALEMENTS PAR MOIS</div>
              <div v-for="p in histogramme" :key="`${p.annee}-${p.mois}`" class="bar">
                <div class="lb"><b>{{ MOIS[p.mois - 1] }}</b><span>{{ p.nombre }}</span></div>
                <div class="trk"><div class="fl n" :style="{ width: (p.nombre / maxHistogramme) * 100 + '%' }"></div></div>
              </div>
              <p v-if="!histogramme.length" style="font-size: 12px; color: var(--mut)">Aucun signalement sur la période.</p>
            </div>
          </template>

          <div style="height: 56px"></div>
        </div>
      </div>
    </div>

    <nav class="tabs">
      <button class="tb" @click="router.push({ name: 'accueil' })"><Icone nom="home" />Accueil</button>
      <button class="tb" @click="router.push({ name: 'signalements' })"><Icone nom="alert" />Signaux</button>
      <button class="tb" @click="router.push({ name: 'slam' })"><Icone nom="climb" />SLAM</button>
      <button class="tb on"><Icone nom="chart" />Tableau</button>
      <button class="tb" @click="router.push({ name: 'assistant-documentaire' })"><Icone nom="chat" />Assistant</button>
      <button class="tb" @click="router.push({ name: 'menu' })"><Icone nom="grid" />Menu</button>
    </nav>
  </div>
</template>

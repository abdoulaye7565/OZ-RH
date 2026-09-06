<script setup>
/**
 * Tableau de bord — vue mobile simplifiée (maquette #s-tdb, figure A.10 du CDC).
 *
 * Écart assumé : la maquette affiche 4 indicateurs (accident avec arrêt,
 * signalements, EPI à vérifier, conformité) dont 3 dépendent de modules qui
 * n'existent pas encore (EPI : lot 2.1, inspections : lot 2.4 ; les accidents
 * du travail avec arrêt ne sont pas non plus suivis comme tels). Plutôt que
 * d'afficher un chiffre inventé, les 4 tuiles montrent les indicateurs
 * réellement calculables aujourd'hui (signalements de la période, à traiter,
 * avancement du plan d'action, actions en retard) — voir docs/JOURNAL.md.
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
</script>

<template>
  <div class="ecran-mobile">
    <BandeauReseau />
    <header class="hd">
      <div class="mk">H</div>
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
              <div class="met"><div class="v">{{ tdb.donnees.signalements.total_periode }}</div><div class="l">signalements</div></div>
              <div class="met a"><div class="v">{{ tdb.donnees.signalements.nombre_a_traiter }}</div><div class="l">à traiter</div></div>
              <div class="met g"><div class="v">{{ Math.round(tdb.donnees.actions.taux_avancement_global * 100) }}%</div><div class="l">actions réalisées</div></div>
              <div class="met a"><div class="v">{{ tdb.donnees.actions.nombre_en_retard }}</div><div class="l">actions en retard</div></div>
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

            <div style="height: 10px"></div>
            <div class="banner info">
              <div>
                Certains indicateurs du cahier des charges (EPI à vérifier, conformité des
                inspections, formations, documents à réviser…) ne sont pas encore disponibles :
                leurs modules ne sont pas encore construits.
              </div>
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
    </nav>
  </div>
</template>

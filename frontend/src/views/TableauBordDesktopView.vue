<script setup>
/**
 * Tableau de bord — vue desktop (maquette #p-dash, figure A.24 du CDC).
 *
 * Écarts assumés, documentés dans docs/JOURNAL.md :
 * - Barre latérale complète de la maquette non reprise (la plupart de ses
 *   liens n'ont pas d'écran) ; remplacée par un bandeau simple.
 * - Les 4 indicateurs de tête sont ceux réellement calculables aujourd'hui
 *   (signalements, à traiter, avancement du plan, actions en retard), pas les
 *   4 de la maquette (accidents, conformité inspections… indisponibles).
 * - "Échéances proches" ne montre que des actions (EPI/formations/documents
 *   n'existent pas encore comme sources d'échéances).
 */
import { computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import Icone from "../components/Icone.vue";
import { useAuthStore } from "../stores/auth";
import { useTableauBordStore } from "../stores/tableauBord";

const router = useRouter();
const auth = useAuthStore();
const tdb = useTableauBordStore();

onMounted(() => tdb.charger());

const MOIS = ["Jan", "Fév", "Mar", "Avr", "Mai", "Juin", "Juil", "Août", "Sep", "Oct", "Nov", "Déc"];

const histogramme = computed(() => (tdb.donnees?.signalements?.par_mois ?? []).slice(-6));
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

function formaterDateCourte(iso) {
  return new Date(iso).toLocaleDateString("fr-FR", { day: "2-digit", month: "2-digit" });
}

function joursRestants(echeance) {
  const jours = Math.ceil((new Date(echeance) - new Date()) / 86400000);
  return jours;
}

function styleEcheance(jours) {
  if (jours < 0) return "t-red";
  if (jours <= 7) return "t-or";
  return "t-gy";
}
</script>

<template>
  <div class="bureau">
    <div class="bureau-entete">
      <h1>Tableau de bord</h1>
      <span class="sub">{{ auth.utilisateur ? `${auth.utilisateur.prenom} ${auth.utilisateur.nom}` : "" }}</span>
      <button class="btn gh" style="width: auto; margin-left: auto" @click="router.push({ name: 'signalements' })">
        <Icone nom="alert" taille="sm" />Signalements
      </button>
    </div>

    <div v-if="tdb.erreur" class="banner err">{{ tdb.erreur }}</div>

    <template v-if="tdb.donnees">
      <div class="mets">
        <div class="met">
          <div class="met-hd"><span class="ic m-or"><Icone nom="alert" taille="sm" /></span>Signalements de la période</div>
          <div class="v">{{ tdb.donnees.signalements.total_periode }}</div>
        </div>
        <div class="met">
          <div class="met-hd"><span class="ic m-red"><Icone nom="search" taille="sm" /></span>Signalements à traiter</div>
          <div class="v">{{ tdb.donnees.signalements.nombre_a_traiter }}</div>
        </div>
        <div class="met">
          <div class="met-hd"><span class="ic m-gd"><Icone nom="check" taille="sm" /></span>Plan d'action réalisé</div>
          <div class="v">{{ Math.round(tdb.donnees.actions.taux_avancement_global * 100) }}%</div>
        </div>
        <div class="met">
          <div class="met-hd"><span class="ic m-bl"><Icone nom="chart" taille="sm" /></span>Actions en retard</div>
          <div class="v">{{ tdb.donnees.actions.nombre_en_retard }}</div>
        </div>
      </div>

      <div class="grid2">
        <div class="card">
          <div class="ch"><Icone nom="chart" /><h3>Signalements par mois</h3></div>
          <div class="cb">
            <div class="bars">
              <div v-for="(p, i) in histogramme" :key="`${p.annee}-${p.mois}`" class="bcol">
                <span class="val">{{ p.nombre }}</span>
                <div
                  class="bar"
                  :class="{ gd: i === histogramme.length - 1 }"
                  :style="{ height: (p.nombre / maxHistogramme) * 130 + 'px' }"
                ></div>
                <span class="lbl">{{ MOIS[p.mois - 1] }}</span>
              </div>
            </div>
            <p v-if="!histogramme.length" style="font-size: 12px; color: var(--mut)">Aucun signalement sur la période.</p>
          </div>
        </div>

        <div class="card">
          <div class="ch"><Icone nom="check" /><h3>Avancement du plan d'action</h3></div>
          <div class="cb" v-if="plan">
            <div style="margin-bottom: 12px">
              <div style="display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 5px">
                <b>Réalisées</b><span style="color: var(--mut)">{{ plan.par_statut.cloturee }} / {{ plan.total }}</span>
              </div>
              <div class="trk"><div class="fl g" :style="{ width: pourcent(plan.par_statut.cloturee, plan.total) + '%' }"></div></div>
            </div>
            <div style="margin-bottom: 12px">
              <div style="display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 5px">
                <b>En cours</b><span style="color: var(--mut)">{{ plan.par_statut.en_cours }} / {{ plan.total }}</span>
              </div>
              <div class="trk"><div class="fl gd" :style="{ width: pourcent(plan.par_statut.en_cours, plan.total) + '%' }"></div></div>
            </div>
            <div style="margin-bottom: 0">
              <div style="display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 5px">
                <b>En retard</b><span style="color: var(--red); font-weight: 650">{{ plan.nombre_en_retard }} / {{ plan.total }}</span>
              </div>
              <div class="trk"><div class="fl o" :style="{ width: pourcent(plan.nombre_en_retard, plan.total) + '%' }"></div></div>
            </div>
          </div>
        </div>
      </div>

      <div class="grid2">
        <div class="card">
          <div class="ch"><Icone nom="alert" /><h3>Signalements à traiter</h3></div>
          <table>
            <thead><tr><th>Référence</th><th>Objet</th><th>Reçu</th><th>Statut</th></tr></thead>
            <tbody>
              <tr v-for="s in tdb.donnees.signalements.a_traiter" :key="s.id">
                <td><b>{{ s.reference ?? "en attente" }}</b></td>
                <td>{{ s.lieu }}<div class="sub">{{ s.description.slice(0, 60) }}</div></td>
                <td>{{ formaterDateCourte(s.date_saisie) }}</td>
                <td><span class="tag" :class="s.statut === 'nouveau' ? 't-red' : 't-gd'">{{ s.statut === "nouveau" ? "Nouveau" : "En analyse" }}</span></td>
              </tr>
              <tr v-if="!tdb.donnees.signalements.a_traiter.length"><td colspan="4" style="color: var(--mut)">Aucun signalement à traiter.</td></tr>
            </tbody>
          </table>
        </div>

        <div class="card">
          <div class="ch"><Icone nom="clock" /><h3>Échéances proches (actions)</h3></div>
          <table>
            <tbody>
              <tr v-for="a in tdb.donnees.echeances_proches" :key="a.id">
                <td>
                  <div class="cellrow">
                    <span class="mini" :class="joursRestants(a.echeance) < 0 ? 'm-red' : 'm-or'"><Icone nom="check" taille="sm" /></span>
                    <div><b>{{ a.libelle }}</b><div class="sub">Échéance {{ formaterDateCourte(a.echeance) }}</div></div>
                  </div>
                </td>
                <td style="text-align: right">
                  <span class="tag" :class="styleEcheance(joursRestants(a.echeance))">
                    {{ joursRestants(a.echeance) < 0 ? `${joursRestants(a.echeance)} j` : `J−${joursRestants(a.echeance)}` }}
                  </span>
                </td>
              </tr>
              <tr v-if="!tdb.donnees.echeances_proches.length"><td style="color: var(--mut)">Aucune échéance proche.</td></tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="banner info">
        <div>
          Indisponibles pour l'instant, faute de module : {{ tdb.donnees.modules_non_disponibles.join(", ") }}.
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
/**
 * Tableau de bord — vue desktop (maquette #p-dash, figure A.24 du CDC).
 *
 * Mis à jour le 2026-09-08 (synchronisation aux données réelles) : les 4
 * indicateurs de tête reprennent maintenant ceux de la maquette (accidents,
 * signalements, plan d'action, conformité inspections) — EPI, Inspections,
 * Formations, Documents et Satisfaction existent depuis le chantier du
 * 2026-09-07 et alimentent chacun un indicateur réel côté API
 * (`tableau_bord_service.py`), plutôt que d'être listés comme indisponibles.
 * Une seconde rangée d'indicateurs (absente de la maquette, qui n'en montre
 * que 4) rend visibles les autres données désormais réelles : séances à
 * venir, personnel formé, documents à réviser, réclamations clients.
 *
 * Écarts encore assumés :
 * - Barre latérale complète de la maquette non reprise ; remplacée par la
 *   barre latérale commune de GestionLayout.vue.
 * - "Accidents avec arrêt" affiché sans la distinction avec/sans arrêt :
 *   aucun champ ne la porte dans le dictionnaire de données du signalement.
 * - Incidents environnementaux et sécurité des données (coffre-fort)
 *   restent sans indicateur, faute de module source — plus signalé par une
 *   banane technique en pied de page, un utilisateur final n'a pas à
 *   connaître l'état d'avancement du développement.
 */
import { computed, onMounted, ref, watch } from "vue";
import Icone from "../components/Icone.vue";
import api from "../services/api";
import { useTableauBordStore } from "../stores/tableauBord";
import { joursRestantsCivil } from "../utils/dates";

const tdb = useTableauBordStore();

// Filtres (revue d'ensemble 2026-09-10) : le back-end acceptait déjà site_id /
// date_debut / date_fin, l'écran ne les exposait pas.
const sites = ref([]);
const siteChoisi = ref("");
const PERIODES = [
  { valeur: "30", libelle: "30 derniers jours" },
  { valeur: "90", libelle: "90 derniers jours" },
  { valeur: "365", libelle: "12 derniers mois" },
  { valeur: "", libelle: "Depuis le début" },
];
const periodeChoisie = ref("90");

function rechargerAvecFiltres() {
  const params = {};
  if (siteChoisi.value) params.siteId = Number(siteChoisi.value);
  if (periodeChoisie.value) {
    const debut = new Date();
    debut.setDate(debut.getDate() - Number(periodeChoisie.value));
    params.dateDebut = debut.toISOString();
  }
  tdb.charger(params);
}

onMounted(async () => {
  rechargerAvecFiltres();
  try {
    sites.value = await api.requete("/api/v1/sites");
  } catch {
    sites.value = [];
  }
});
watch([siteChoisi, periodeChoisie], rechargerAvecFiltres);

const MOIS = ["Jan", "Fév", "Mar", "Avr", "Mai", "Juin", "Juil", "Août", "Sep", "Oct", "Nov", "Déc"];

const histogramme = computed(() => (tdb.donnees?.signalements?.par_mois ?? []).slice(-6));
const maxHistogramme = computed(() => Math.max(1, ...histogramme.value.map((p) => p.nombre)));

const plan = computed(() => {
  const a = tdb.donnees?.actions;
  if (!a) return null;
  const total = Object.values(a.par_statut).reduce((s, n) => s + n, 0);
  return { ...a, total };
});
// Histogramme "Avancement du plan d'action" (2026-09-09, retour direct de
// l'utilisateur — "le tableau de bord doit avoir des histogrammes") : les 3
// colonnes ne totalisent pas forcément `plan.total` (nombre_en_retard n'est
// pas un statut à part, c'est un sous-ensemble d'actions déjà ouvertes/en
// cours dépassant leur échéance) — le maximum des 3 valeurs sert donc
// d'échelle, pas le total.
const maxPlan = computed(() => {
  if (!plan.value) return 1;
  return Math.max(1, plan.value.par_statut.cloturee, plan.value.par_statut.en_cours, plan.value.nombre_en_retard);
});

function formaterDateCourte(iso) {
  return new Date(iso).toLocaleDateString("fr-FR", { day: "2-digit", month: "2-digit" });
}

// Une échéance (a.echeance) est une date civile, pas un horodatage : voir
// utils/dates.js — new Date(echeance) seul décale parfois d'un jour.
const joursRestants = joursRestantsCivil;

function formaterEcheanceCourte(echeance) {
  const [annee, mois, jour] = echeance.slice(0, 10).split("-").map(Number);
  return new Date(annee, mois - 1, jour).toLocaleDateString("fr-FR", { day: "2-digit", month: "2-digit" });
}

function styleEcheance(jours) {
  if (jours < 0) return "t-red";
  if (jours <= 7) return "t-or";
  return "t-gy";
}

const ICONE_ECHEANCE = { action: "check", epi: "vest", document: "doc", formation: "cap" };
const COULEUR_ECHEANCE = { action: "m-bl", epi: "m-or", document: "m-gd", formation: "m-bl" };

const conformiteInspectionsPourcent = computed(() => {
  const taux = tdb.donnees?.inspections?.taux_conformite_moyen;
  return taux === null || taux === undefined ? null : Math.round(taux * 100);
});
</script>

<template>
  <div>
    <div class="filters">
      <select v-model="siteChoisi" class="inp" style="width: auto; height: 32px; padding: 0 10px">
        <option value="">Tous les sites</option>
        <option v-for="s in sites" :key="s.id" :value="s.id">{{ s.nom }}</option>
      </select>
      <select v-model="periodeChoisie" class="inp" style="width: auto; height: 32px; padding: 0 10px">
        <option v-for="p in PERIODES" :key="p.valeur" :value="p.valeur">{{ p.libelle }}</option>
      </select>
      <span v-if="tdb.chargement" class="sub" style="align-self: center">Actualisation…</span>
    </div>

    <div v-if="tdb.erreur" class="banner err">{{ tdb.erreur }}</div>
    <div v-else-if="!tdb.donnees && tdb.chargement" class="skel" style="height: 120px"></div>

    <template v-if="tdb.donnees">
      <div class="mets">
        <div class="met">
          <div class="met-hd">
            <span class="ic" :class="tdb.donnees.securite.accidents_periode > 0 ? 'm-red' : 'm-gr'"><Icone nom="shield" taille="sm" /></span>
            Accidents (période)
          </div>
          <div class="v">{{ tdb.donnees.securite.accidents_periode }}</div>
          <div v-if="tdb.donnees.securite.jours_sans_accident !== null" class="sub" style="font-size: 11px; color: var(--mut); margin-top: 2px">
            {{ tdb.donnees.securite.jours_sans_accident }} jours sans accident
          </div>
        </div>
        <div class="met">
          <div class="met-hd"><span class="ic m-or"><Icone nom="alert" taille="sm" /></span>Signalements de la période</div>
          <div class="v">{{ tdb.donnees.signalements.total_periode }}</div>
        </div>
        <div class="met">
          <div class="met-hd"><span class="ic m-gd"><Icone nom="check" taille="sm" /></span>Plan d'action réalisé</div>
          <div class="v">{{ Math.round(tdb.donnees.actions.taux_avancement_global * 100) }}%</div>
        </div>
        <div class="met">
          <div class="met-hd"><span class="ic" :class="conformiteInspectionsPourcent !== null && conformiteInspectionsPourcent < 90 ? 'm-or' : 'm-bl'"><Icone nom="clip" taille="sm" /></span>Conformité inspections</div>
          <div class="v">{{ conformiteInspectionsPourcent !== null ? `${conformiteInspectionsPourcent}%` : "—" }}</div>
          <div class="sub" style="font-size: 11px; color: var(--mut); margin-top: 2px">{{ tdb.donnees.inspections.realisees_periode }} réalisées sur la période</div>
        </div>
      </div>

      <div class="mets" style="margin-top: 12px">
        <div class="met">
          <div class="met-hd"><span class="ic m-bl"><Icone nom="cap" taille="sm" /></span>Personnel formé</div>
          <div class="v">{{ tdb.donnees.formations.personnel_forme }} / {{ tdb.donnees.formations.personnel_total }}</div>
        </div>
        <div class="met">
          <div class="met-hd"><span class="ic m-gd"><Icone nom="calendar" taille="sm" /></span>Sensibilisations à venir</div>
          <div class="v">{{ tdb.donnees.formations.seances_a_venir }}</div>
        </div>
        <div class="met">
          <div class="met-hd"><span class="ic m-or"><Icone nom="doc" taille="sm" /></span>Documents à réviser</div>
          <div class="v">{{ tdb.donnees.documents.a_reviser_bientot }}</div>
        </div>
        <div class="met">
          <div class="met-hd"><span class="ic" :class="tdb.donnees.satisfaction.reclamations_periode > 0 ? 'm-red' : 'm-gr'"><Icone nom="star" taille="sm" /></span>Réclamations clients</div>
          <div class="v">{{ tdb.donnees.satisfaction.reclamations_periode }}</div>
          <div v-if="tdb.donnees.satisfaction.note_moyenne !== null" class="sub" style="font-size: 11px; color: var(--mut); margin-top: 2px">
            note moyenne {{ tdb.donnees.satisfaction.note_moyenne.toFixed(1) }} / 5
          </div>
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
            <div class="bars">
              <div class="bcol">
                <span class="val">{{ plan.par_statut.cloturee }}</span>
                <div class="bar g" :style="{ height: (plan.par_statut.cloturee / maxPlan) * 130 + 'px' }"></div>
                <span class="lbl">Réalisées</span>
              </div>
              <div class="bcol">
                <span class="val">{{ plan.par_statut.en_cours }}</span>
                <div class="bar gd" :style="{ height: (plan.par_statut.en_cours / maxPlan) * 130 + 'px' }"></div>
                <span class="lbl">En cours</span>
              </div>
              <div class="bcol">
                <span class="val" :style="plan.nombre_en_retard ? 'color:var(--red)' : ''">{{ plan.nombre_en_retard }}</span>
                <div class="bar o" :style="{ height: (plan.nombre_en_retard / maxPlan) * 130 + 'px' }"></div>
                <span class="lbl">En retard</span>
              </div>
            </div>
            <p style="font-size: 11px; color: var(--mut); margin: 6px 0 0; text-align: center">{{ plan.total }} actions au total</p>
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
          <div class="ch"><Icone nom="clock" /><h3>Échéances proches</h3></div>
          <table>
            <tbody>
              <tr v-for="(a, i) in tdb.donnees.echeances_proches" :key="`${a.type}-${a.reference}-${a.echeance}-${i}`">
                <td>
                  <div class="cellrow">
                    <span class="mini" :class="joursRestants(a.echeance) < 0 ? 'm-red' : COULEUR_ECHEANCE[a.type]"><Icone :nom="ICONE_ECHEANCE[a.type]" taille="sm" /></span>
                    <div><b>{{ a.libelle }}</b><div class="sub">Échéance {{ formaterEcheanceCourte(a.echeance) }}</div></div>
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
    </template>
  </div>
</template>

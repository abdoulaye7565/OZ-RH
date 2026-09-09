<script setup>
/**
 * Inspections — vue desktop (maquette #p-insp).
 *
 * Écart assumé : la fiche de saisie (clic sur une ligne, ou "Nouvelle
 * inspection") réutilise l'écran mobile InspectionDetailView.vue plutôt
 * qu'un écran desktop dédié — même compromis que Parc & configurations
 * (ParcDesktopView -> ParcFicheView) : la checklist reste pleinement
 * fonctionnelle, seulement pas encore habillée au style desktop.
 */
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import Icone from "../components/Icone.vue";
import { TYPES_INSPECTION, useInspectionsStore } from "../stores/inspections";
import { formaterDateCivile } from "../utils/dates";

const router = useRouter();
const inspections = useInspectionsStore();
onMounted(() => inspections.charger());

const filtreType = ref("Tous");
const listeFiltree = computed(() =>
  filtreType.value === "Tous" ? inspections.liste : inspections.liste.filter((i) => i.modele === filtreType.value)
);

function couleurTaux(taux) {
  if (taux === null || taux === undefined) return "g";
  if (taux >= 90) return "g";
  if (taux >= 70) return "o";
  return "red";
}
// Inspection.taux_conformite (API, table "Inspections réalisées") est une
// fraction 0-1 — `inspections.tauxParType` (magasin), lui, est déjà en
// pourcentage 0-100 (voir stores/inspections.js) : ne pas reconvertir celui-là.
function pourcent(taux) {
  return taux === null || taux === undefined ? null : Math.round(taux * 100);
}
function tagEcarts(insp) {
  const nc = insp.points.filter((p) => p.cotation === "NC").length;
  if (nc === 0) return { classe: "t-gr", libelle: "Aucun" };
  return { classe: nc >= 3 ? "t-red" : "t-or", libelle: `${nc} écart${nc > 1 ? "s" : ""}` };
}

const formulaireOuvert = ref(false);
const modeleChoisi = ref("locaux");
const siteChoisi = ref("");
function demarrer() {
  router.push({ name: "inspection-nouvelle", query: { modele: modeleChoisi.value, site_id: siteChoisi.value } });
}
</script>

<template>
  <div>
    <div v-if="inspections.erreur" class="banner err">{{ inspections.erreur }}</div>

    <div class="filters">
      <button class="seg" :class="{ on: filtreType === 'Tous' }" @click="filtreType = 'Tous'">Toutes · {{ inspections.liste.length }}</button>
      <button v-for="t in TYPES_INSPECTION" :key="t.valeur" class="seg" :class="{ on: filtreType === t.valeur }" @click="filtreType = t.valeur">
        {{ t.abrege }}
      </button>
      <span style="flex: 1"></span>
      <button class="btn pri sm" style="width: auto" @click="formulaireOuvert = !formulaireOuvert">
        <Icone nom="plus" taille="sm" />Nouvelle inspection
      </button>
    </div>

    <div v-if="formulaireOuvert" class="card">
      <div class="ch"><h3>Nouvelle inspection</h3></div>
      <div class="cb">
        <div class="grid2">
          <div>
            <label class="f">Type d'inspection</label>
            <select v-model="modeleChoisi" class="inp">
              <option v-for="t in TYPES_INSPECTION" :key="t.valeur" :value="t.valeur">{{ t.libelle }}</option>
            </select>
          </div>
          <div>
            <label class="f">Site</label>
            <select v-model="siteChoisi" class="inp">
              <option value="" disabled>Choisir…</option>
              <option v-for="s in inspections.sites" :key="s.id" :value="s.id">{{ s.nom }}</option>
            </select>
          </div>
        </div>
        <button class="btn pri" style="width: auto; margin-top: 10px" :disabled="!siteChoisi" @click="demarrer">Démarrer</button>
      </div>
    </div>

    <div class="grid2" style="grid-template-columns: 1fr 1fr">
      <div class="card">
        <div class="ch"><Icone nom="chart" style="color: var(--navy2)" /><h3>Conformité par type d'inspection</h3></div>
        <div class="cb">
          <div v-for="t in TYPES_INSPECTION" :key="t.valeur" style="margin-bottom: 12px">
            <div style="display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 5px">
              <b>{{ t.libelle }}</b>
              <span :style="{ color: inspections.tauxParType[t.valeur] === undefined ? 'var(--mut)' : couleurTaux(inspections.tauxParType[t.valeur]) === 'o' ? 'var(--orange)' : 'var(--mut)' }">
                {{ inspections.tauxParType[t.valeur] !== undefined ? `${inspections.tauxParType[t.valeur].toFixed(0)} %` : "—" }}
              </span>
            </div>
            <div class="trk">
              <div
                class="fl"
                :class="couleurTaux(inspections.tauxParType[t.valeur])"
                :style="{ width: `${inspections.tauxParType[t.valeur] ?? 0}%` }"
              ></div>
            </div>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="ch"><Icone nom="calendar" style="color: var(--orange)" /><h3>Inspections à planifier</h3></div>
        <table>
          <tbody>
            <tr v-for="p in inspections.planification" :key="`${p.site_id}-${p.modele}`">
              <td>
                <div class="cellrow">
                  <span class="mini" :class="p.due ? 'm-or' : 'm-bl'"><Icone nom="clip" taille="sm" /></span>
                  <div>
                    <b>{{ inspections.libelleType(p.modele) }} — {{ inspections.nomSite(p.site_id) ?? `Site #${p.site_id}` }}</b>
                    <div class="sub">dernière le {{ formaterDateCivile(p.derniere_inspection_le) }}</div>
                  </div>
                </div>
              </td>
              <td style="text-align: right">
                <span class="tag" :class="p.due ? 't-or' : 't-bl'">{{ p.jours_restants < 0 ? "En retard" : `J−${p.jours_restants}` }}</span>
              </td>
            </tr>
            <tr v-if="!inspections.planification.length"><td style="color: var(--mut)">Rien de planifié dans l'horizon.</td></tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="card">
      <div class="ch"><h3>Inspections réalisées</h3></div>
      <table>
        <thead><tr><th>Réf.</th><th>Type</th><th>Site / Objet</th><th>Inspecteur</th><th>Date</th><th style="width: 120px">Conformité</th><th>Écarts</th><th>Statut</th></tr></thead>
        <tbody>
          <tr
            v-for="i in listeFiltree"
            :key="i.id"
            style="cursor: pointer"
            @click="router.push({ name: 'inspection-detail', params: { id: i.id } })"
          >
            <td><b>{{ i.reference ?? `#${i.id}` }}</b></td>
            <td>{{ inspections.libelleType(i.modele) }}</td>
            <td>{{ inspections.nomSite(i.site_id) ?? `Site #${i.site_id}` }}</td>
            <td>{{ inspections.nomUtilisateur(i.inspecteur_id) ?? `Utilisateur #${i.inspecteur_id}` }}</td>
            <td>{{ formaterDateCivile(i.date) }}</td>
            <td>
              <template v-if="i.taux_conformite !== null">
                <div class="trk"><div class="fl" :class="couleurTaux(pourcent(i.taux_conformite))" :style="{ width: `${pourcent(i.taux_conformite)}%` }"></div></div>
                <div class="sub">{{ pourcent(i.taux_conformite) }} %</div>
              </template>
              <span v-else style="color: var(--mut)">—</span>
            </td>
            <td><span class="tag" :class="tagEcarts(i).classe">{{ tagEcarts(i).libelle }}</span></td>
            <td><span class="tag" :class="i.statut === 'cloturee' ? 't-gr' : 't-gd'">{{ i.statut === "cloturee" ? "Clôturée" : "En cours" }}</span></td>
          </tr>
          <tr v-if="!inspections.chargement && !listeFiltree.length"><td colspan="8" style="color: var(--mut)">Aucune inspection.</td></tr>
        </tbody>
      </table>
      <div class="pagin"><span>{{ listeFiltree.length }} inspections · les écarts créent automatiquement des actions</span></div>
    </div>
  </div>
</template>

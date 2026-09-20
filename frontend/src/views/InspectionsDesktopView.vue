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
import BarrePagination from "../components/BarrePagination.vue";
import Icone from "../components/Icone.vue";
import Modal from "../components/Modal.vue";
import { useRechercheEtPagination } from "../composables/useRechercheEtPagination";
import { TYPES_INSPECTION, useInspectionsStore } from "../stores/inspections";
import { formaterDateCivile } from "../utils/dates";
import { telechargerPdf } from "../utils/telechargement";

const router = useRouter();
const inspections = useInspectionsStore();
onMounted(() => inspections.charger());

const filtreType = ref("Tous");
const listeFiltree = computed(() =>
  filtreType.value === "Tous" ? inspections.liste : inspections.liste.filter((i) => i.modele === filtreType.value)
);

function correspond(i, terme) {
  return (
    String(i.reference ?? "").toLowerCase().includes(terme) ||
    inspections.libelleType(i.modele).toLowerCase().includes(terme) ||
    (i.objet_inspecte ?? "").toLowerCase().includes(terme) ||
    (i.equipement_id ? (inspections.nomEquipement(i.equipement_id) ?? "") : "").toLowerCase().includes(terme) ||
    (inspections.nomSite(i.site_id) ?? "").toLowerCase().includes(terme) ||
    (inspections.nomUtilisateur(i.inspecteur_id) ?? "").toLowerCase().includes(terme)
  );
}
const { recherche, page, totalPages, resultats, elementsPage, allerPage } =
  useRechercheEtPagination(listeFiltree, correspond, 12);

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
const equipementChoisi = ref("");
const objetInspecte = ref("");

// Équipements du site retenu (un équipement appartient à un site) : inutile
// de proposer un équipement d'un autre site pour une inspection donnée.
const equipementsDuSite = computed(() =>
  siteChoisi.value ? inspections.equipements.filter((e) => e.site_id === Number(siteChoisi.value)) : []
);

// Repère de l'objet inspecté selon le type (retour utilisateur 2026-09-10 :
// "après inspection d'un extincteur, on ne sait pas lequel").
const PLACEHOLDER_OBJET = {
  incendie: "Ex. Extincteur EXT-03, hall RDC",
  electricite: "Ex. Tableau TGBT, local technique",
  installations: "Ex. Ligne de vie toiture nord",
  locaux: "Ex. Poste de travail bureau 2",
  equipements: "Repère complémentaire (facultatif)",
};

const pdfEnCours = ref(null);
async function telechargerInspection(i) {
  pdfEnCours.value = i.id;
  try {
    await telechargerPdf(`/api/v1/inspections/${i.id}/export-pdf`, `${i.reference ?? "inspection-" + i.id}.pdf`);
  } catch (e) {
    inspections.erreur = e?.message ?? "Téléchargement du PDF impossible";
  } finally {
    pdfEnCours.value = null;
  }
}

function demarrer() {
  const query = { modele: modeleChoisi.value, site_id: siteChoisi.value };
  if (modeleChoisi.value === "equipements" && equipementChoisi.value) {
    query.equipement_id = equipementChoisi.value;
  }
  if (objetInspecte.value.trim()) query.objet_inspecte = objetInspecte.value.trim();
  router.push({ name: "inspection-nouvelle", query });
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
      <div class="srch">
        <Icone nom="search" taille="sm" />
        <input v-model="recherche" placeholder="Rechercher une réf., un objet, un site…" />
      </div>
      <button class="btn pri sm" style="width: auto" @click="formulaireOuvert = true">
        <Icone nom="plus" taille="sm" />Nouvelle inspection
      </button>
    </div>

    <Modal v-if="formulaireOuvert" titre="Nouvelle inspection" @fermer="formulaireOuvert = false">
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
      <template v-if="modeleChoisi === 'equipements'">
        <label class="f">Équipement inspecté (facultatif)</label>
        <select v-model="equipementChoisi" class="inp" :disabled="!siteChoisi">
          <option value="">Aucun en particulier</option>
          <option v-for="e in equipementsDuSite" :key="e.id" :value="e.id">
            {{ e.identity }} — {{ e.marque }} {{ e.modele }}<template v-if="e.emplacement"> ({{ e.emplacement }})</template>
          </option>
        </select>
        <p v-if="siteChoisi && !equipementsDuSite.length" class="sub" style="margin-top: 4px">
          Aucun équipement enregistré pour ce site.
        </p>
      </template>
      <label class="f">
        Objet / repère inspecté
        <template v-if="modeleChoisi !== 'equipements'"> (recommandé)</template>
        <template v-else> (facultatif)</template>
      </label>
      <input v-model="objetInspecte" class="inp" :placeholder="PLACEHOLDER_OBJET[modeleChoisi]" />
      <p class="sub" style="margin-top: 4px">
        Identifie précisément ce qui a été inspecté (extincteur, tableau, ligne de vie…) — sinon on ne saura pas lequel.
      </p>
      <div style="display: flex; gap: 8px; margin-top: 10px">
        <button class="btn pri" style="width: auto" :disabled="!siteChoisi" @click="demarrer">Démarrer</button>
        <button class="btn gh" style="width: auto" @click="formulaireOuvert = false">Annuler</button>
      </div>
    </Modal>

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
        <thead><tr><th>Réf.</th><th>Type</th><th>Site / Objet</th><th>Inspecteur</th><th>Date</th><th style="width: 120px">Conformité</th><th>Écarts</th><th>Statut</th><th></th></tr></thead>
        <tbody>
          <tr
            v-for="i in elementsPage"
            :key="i.id"
            style="cursor: pointer"
            @click="router.push({ name: 'inspection-detail', params: { id: i.id } })"
          >
            <td><b>{{ i.reference ?? `#${i.id}` }}</b></td>
            <td>{{ inspections.libelleType(i.modele) }}</td>
            <td>
              <template v-if="i.equipement_id || i.objet_inspecte">
                <b>{{ i.equipement_id ? (inspections.nomEquipement(i.equipement_id) ?? `Équipement #${i.equipement_id}`) : i.objet_inspecte }}</b>
                <div class="sub">
                  {{ inspections.nomSite(i.site_id) ?? `Site #${i.site_id}` }}
                  <template v-if="i.equipement_id && i.objet_inspecte"> · {{ i.objet_inspecte }}</template>
                </div>
              </template>
              <template v-else>{{ inspections.nomSite(i.site_id) ?? `Site #${i.site_id}` }}</template>
            </td>
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
            <td style="text-align: right">
              <button class="btn gh sm" style="width: auto" :disabled="pdfEnCours === i.id" @click.stop="telechargerInspection(i)">
                <Icone nom="dl" taille="sm" />PDF
              </button>
            </td>
          </tr>
          <tr v-if="!inspections.chargement && !listeFiltree.length"><td colspan="9" style="color: var(--mut)">Aucune inspection.</td></tr>
          <tr v-if="listeFiltree.length && !resultats.length"><td colspan="9" style="color: var(--mut)">Aucune inspection ne correspond à la recherche.</td></tr>
        </tbody>
      </table>
      <BarrePagination :page="page" :total-pages="totalPages" @changer="allerPage">
        {{ resultats.length }} sur {{ inspections.liste.length }} inspection{{ inspections.liste.length > 1 ? "s" : "" }} · les écarts créent automatiquement des actions
      </BarrePagination>
    </div>
  </div>
</template>

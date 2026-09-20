<script setup>
/**
 * Inspections — vue mobile, écran de liste + démarrage (maquette #s-insp,
 * qui ne montre que la fiche d'une inspection en cours — la liste et le
 * choix du modèle n'ont pas de fragment dédié, construits ici en reprenant
 * le langage déjà établi (métriques + liste + formulaire, comme Risques/
 * Permis) : sans cet écran, `POST /inspections` resterait inatteignable
 * depuis le mobile).
 */
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import Icone from "../components/Icone.vue";
import Modal from "../components/Modal.vue";
import BandeauReseau from "../components/BandeauReseau.vue";
import { TYPES_INSPECTION, useInspectionsStore } from "../stores/inspections";
import { formaterDateCivile } from "../utils/dates";

const router = useRouter();
const inspections = useInspectionsStore();
onMounted(() => inspections.charger());

const enCours = computed(() => inspections.liste.filter((i) => i.statut === "en_cours").length);

const STYLE_STATUT = { en_cours: { tag: "t-bl", libelle: "EN COURS" }, cloturee: { tag: "t-gr", libelle: "CLÔTURÉE" } };

// Inspection.taux_conformite (API) est une fraction 0-1 — converti en
// pourcentage 0-100 ici, seule unité affichée à l'écran.
function pourcent(taux) {
  return taux === null || taux === undefined ? null : Math.round(taux * 100);
}

function tagConformite(taux) {
  const p = pourcent(taux);
  if (p === null) return "t-gy";
  if (p >= 90) return "t-gr";
  if (p >= 70) return "t-or";
  return "t-red";
}

// --- Démarrer une nouvelle inspection ---
const formulaireOuvert = ref(false);
const modeleChoisi = ref("locaux");
const siteChoisi = ref("");
const equipementChoisi = ref("");
const objetInspecte = ref("");

// Un équipement appartient à un site : ne proposer que ceux du site retenu.
const equipementsDuSite = computed(() =>
  siteChoisi.value ? inspections.equipements.filter((e) => e.site_id === Number(siteChoisi.value)) : []
);

function demarrer() {
  const query = { modele: modeleChoisi.value, site_id: siteChoisi.value };
  if (modeleChoisi.value === "equipements" && equipementChoisi.value) query.equipement_id = equipementChoisi.value;
  if (objetInspecte.value.trim()) query.objet_inspecte = objetInspecte.value.trim();
  router.push({ name: "inspection-nouvelle", query });
}
</script>

<template>
  <div class="ecran-mobile">
    <BandeauReseau />
    <header class="hd">
      <button class="back" aria-label="Retour" @click="router.push({ name: 'menu' })"><Icone nom="back" /></button>
      <div>
        <h1>Inspections</h1>
        <div class="sub">{{ enCours }} en cours · {{ inspections.liste.length }} au total</div>
      </div>
    </header>

    <div class="wrap">
      <div class="body">
        <div class="pad">
          <div v-if="inspections.erreur" class="banner err">{{ inspections.erreur }}</div>
          <div v-else-if="inspections.chargement" class="skel" style="height: 64px"></div>

          <template v-if="inspections.planification.some((p) => p.due)">
            <div class="sec">À PLANIFIER</div>
            <div v-for="p in inspections.planification.filter((p) => p.due)" :key="`${p.site_id}-${p.modele}`" class="row">
              <span class="lead or"><Icone nom="clock" /></span>
              <div class="tx">
                <b>{{ inspections.libelleType(p.modele) }}</b>
                <div class="meta">
                  <span>{{ inspections.nomSite(p.site_id) ?? `Site #${p.site_id}` }}</span>
                  <span>Dernière le {{ formaterDateCivile(p.derniere_inspection_le) }}</span>
                </div>
              </div>
              <span class="tag t-or">{{ p.jours_restants < 0 ? "En retard" : `J−${p.jours_restants}` }}</span>
            </div>
          </template>

          <div class="sec" style="margin-top: 10px">INSPECTIONS RÉALISÉES</div>
          <div
            v-for="i in inspections.liste"
            :key="i.id"
            class="row"
            role="button"
            tabindex="0"
            @click="router.push({ name: 'inspection-detail', params: { id: i.id } })"
            @keydown.enter="router.push({ name: 'inspection-detail', params: { id: i.id } })"
          >
            <span class="lead nv"><Icone nom="clip" /></span>
            <div class="tx">
              <b>{{ i.reference ?? `Inspection #${i.id}` }} — {{ inspections.libelleType(i.modele) }}</b>
              <div v-if="i.equipement_id || i.objet_inspecte" class="meta">
                <span>{{ i.equipement_id ? (inspections.nomEquipement(i.equipement_id) ?? `Équipement #${i.equipement_id}`) : i.objet_inspecte }}</span>
              </div>
              <div class="meta">
                <span>{{ inspections.nomSite(i.site_id) ?? `Site #${i.site_id}` }}</span>
                <span>{{ inspections.nomUtilisateur(i.inspecteur_id) ?? `Inspecteur #${i.inspecteur_id}` }}</span>
                <span>{{ formaterDateCivile(i.date) }}</span>
                <span v-if="i.taux_conformite !== null">{{ pourcent(i.taux_conformite) }} % conforme</span>
              </div>
            </div>
            <span class="tag" :class="i.statut === 'en_cours' ? 't-bl' : tagConformite(i.taux_conformite)">
              {{ i.statut === "en_cours" ? "EN COURS" : STYLE_STATUT.cloturee.libelle }}
            </span>
          </div>

          <div v-if="!inspections.chargement && !inspections.liste.length" class="empty">
            <div class="ic"><Icone nom="clip" taille="lg" /></div>
            <b>Aucune inspection</b>
          </div>

          <div style="height: 12px"></div>
          <button class="btn pri" @click="formulaireOuvert = true">
            <Icone nom="plus" taille="sm" />Nouvelle inspection
          </button>

          <Modal v-if="formulaireOuvert" titre="Nouvelle inspection" @fermer="formulaireOuvert = false">
            <label class="f">Type d'inspection</label>
            <select v-model="modeleChoisi" class="inp">
              <option v-for="t in TYPES_INSPECTION" :key="t.valeur" :value="t.valeur">{{ t.libelle }}</option>
            </select>
            <label class="f">Site</label>
            <select v-model="siteChoisi" class="inp">
              <option value="" disabled>Sélectionner…</option>
              <option v-for="s in inspections.sites" :key="s.id" :value="s.id">{{ s.nom }}</option>
            </select>
            <template v-if="modeleChoisi === 'equipements'">
              <label class="f">Équipement inspecté (facultatif)</label>
              <select v-model="equipementChoisi" class="inp" :disabled="!siteChoisi">
                <option value="">Aucun en particulier</option>
                <option v-for="e in equipementsDuSite" :key="e.id" :value="e.id">
                  {{ e.identity }} — {{ e.marque }} {{ e.modele }}
                </option>
              </select>
              <p v-if="siteChoisi && !equipementsDuSite.length" class="sub" style="margin-top: 4px">
                Aucun équipement enregistré pour ce site.
              </p>
            </template>
            <label class="f">Objet / repère inspecté{{ modeleChoisi === "equipements" ? " (facultatif)" : " (recommandé)" }}</label>
            <input v-model="objetInspecte" class="inp" placeholder="Ex. Extincteur EXT-03, hall RDC" />
            <p class="sub" style="margin-top: 4px">Sinon on ne saura pas lequel a été inspecté.</p>
            <div class="btnrow" style="margin-top: 8px">
              <button class="btn pri sm" style="width: auto" :disabled="!siteChoisi" @click="demarrer">Démarrer</button>
              <button class="btn gh sm" style="width: auto" @click="formulaireOuvert = false">Annuler</button>
            </div>
          </Modal>

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

<script setup>
/**
 * Parc & configurations — vue desktop (maquette #p-parc).
 *
 * Écart assumé : la fiche équipement (clic sur une ligne) réutilise l'écran
 * mobile ParcFicheView.vue plutôt qu'un écran desktop dédié — construire les
 * deux fiches en parallèle aurait retardé les modules encore non commencés ;
 * la fiche mobile reste pleinement fonctionnelle, seulement pas habillée au
 * style desktop.
 *
 * Édition + import ajoutés le 2026-09-19 (revue de compatibilité front/back,
 * "tu corriges tout") : PATCH /equipements/{id} et POST /equipements/import
 * existaient côté serveur (testés) sans UI. Gardes locales alignées sur les
 * permissions réelles du module — GERER_PARC = (technicien, administrateur),
 * pas (referent_sheq, administrateur) comme la plupart des autres modules de
 * gestion (le CDC confie explicitement le parc au technicien, §6 de
 * CLAUDE.md) ; IMPORTER_PARC = (responsable, administrateur), plus
 * restrictif et distinct. Le bouton "Nouvel équipement", jusqu'ici sans
 * aucune garde, en profite pour être corrigé au passage.
 */
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import BarrePagination from "../components/BarrePagination.vue";
import Icone from "../components/Icone.vue";
import Modal from "../components/Modal.vue";
import { useRechercheEtPagination } from "../composables/useRechercheEtPagination";
import { useAuthStore } from "../stores/auth";
import { useParcStore } from "../stores/parc";
import { formaterDateCivile } from "../utils/dates";

const router = useRouter();
const auth = useAuthStore();
const parc = useParcStore();
onMounted(() => parc.charger());

const peutGerer = computed(() => ["technicien", "administrateur"].includes(auth.utilisateur?.role));
const peutImporter = computed(() => ["responsable", "administrateur"].includes(auth.utilisateur?.role));

const MARQUES = ["MikroTik", "Grandstream", "Ubiquiti", "Ruijie", "autre"];
const filtreMarque = ref("Tous");
const listeFiltree = computed(() => (filtreMarque.value === "Tous" ? parc.liste : parc.liste.filter((e) => e.marque === filtreMarque.value)));

function correspond(e, terme) {
  return (
    e.identity?.toLowerCase().includes(terme) ||
    e.modele?.toLowerCase().includes(terme) ||
    e.marque?.toLowerCase().includes(terme) ||
    e.numero_serie?.toLowerCase().includes(terme) ||
    e.emplacement?.toLowerCase().includes(terme) ||
    (parc.nomSite(e.site_id) ?? "").toLowerCase().includes(terme)
  );
}
const { recherche, page, totalPages, resultats, elementsPage, allerPage } =
  useRechercheEtPagination(listeFiltree, correspond, 12);

const formulaireOuvert = ref(false);
const nouveau = ref({ identity: "", marque: "MikroTik", modele: "", numero_serie: "", site_id: "", emplacement: "", date_installation: "" });
const erreurFormulaire = ref(null);

async function soumettre() {
  erreurFormulaire.value = null;
  try {
    await parc.creerEquipement({ ...nouveau.value, site_id: Number(nouveau.value.site_id) });
    formulaireOuvert.value = false;
    nouveau.value = { identity: "", marque: "MikroTik", modele: "", numero_serie: "", site_id: "", emplacement: "", date_installation: "" };
  } catch (e) {
    erreurFormulaire.value = e?.message ?? "Impossible d'enregistrer cet équipement";
  }
}

// --- Édition d'un équipement existant (2026-09-19) ---
const edition = ref(null);
const champsEdition = ref({ identity: "", marque: "MikroTik", modele: "", numero_serie: "", site_id: "", emplacement: "", date_installation: "" });
const erreurEdition = ref(null);
function ouvrirEdition(e) {
  edition.value = e;
  champsEdition.value = {
    identity: e.identity, marque: e.marque, modele: e.modele, numero_serie: e.numero_serie,
    site_id: e.site_id, emplacement: e.emplacement, date_installation: e.date_installation,
  };
  erreurEdition.value = null;
}
async function soumettreEdition() {
  erreurEdition.value = null;
  try {
    await parc.modifierEquipement(edition.value.id, { ...champsEdition.value, site_id: Number(champsEdition.value.site_id) });
    edition.value = null;
  } catch (e) {
    erreurEdition.value = e?.message ?? "Impossible d'enregistrer la correction";
  }
}

// --- Import en masse (2026-09-19) ---
const importOuvert = ref(false);
const fichierImport = ref(null);
const rapportImport = ref(null);
const erreurImport = ref(null);
const importEnCours = ref(false);
function ouvrirImport() {
  importOuvert.value = true;
  fichierImport.value = null;
  rapportImport.value = null;
  erreurImport.value = null;
}
async function soumettreImport() {
  if (!fichierImport.value) {
    erreurImport.value = "Choisissez un fichier .csv ou .xlsx.";
    return;
  }
  erreurImport.value = null;
  importEnCours.value = true;
  try {
    rapportImport.value = await parc.importerParc(fichierImport.value);
  } catch (e) {
    erreurImport.value = e?.message ?? "Impossible d'importer ce fichier";
  } finally {
    importEnCours.value = false;
  }
}
</script>

<template>
  <div>
    <div v-if="parc.erreur" class="banner err">{{ parc.erreur }}</div>

    <div class="filters">
      <button class="seg" :class="{ on: filtreMarque === 'Tous' }" @click="filtreMarque = 'Tous'">Tous · {{ parc.liste.length }}</button>
      <button v-for="m in MARQUES" :key="m" class="seg" :class="{ on: filtreMarque === m }" @click="filtreMarque = m">{{ m }}</button>
      <span style="flex: 1"></span>
      <div class="srch">
        <Icone nom="search" taille="sm" />
        <input v-model="recherche" placeholder="Rechercher un équipement, un site…" />
      </div>
      <button v-if="peutImporter" class="btn gh sm" style="width: auto" @click="ouvrirImport"><Icone nom="dl" taille="sm" />Importer</button>
      <button v-if="peutGerer" class="btn pri sm" style="width: auto" @click="formulaireOuvert = true"><Icone nom="plus" taille="sm" />Nouvel équipement</button>
    </div>

    <Modal v-if="formulaireOuvert" titre="Nouvel équipement" @fermer="formulaireOuvert = false">
      <div class="grid2">
        <div>
          <label class="f">Identity (SITE-FONCTION-NN)</label>
          <input v-model="nouveau.identity" class="inp" placeholder="Ex. KAT-ST-01" />
          <label class="f">Marque</label>
          <select v-model="nouveau.marque" class="inp"><option v-for="m in MARQUES" :key="m" :value="m">{{ m }}</option></select>
          <label class="f">Modèle</label>
          <input v-model="nouveau.modele" class="inp" />
          <label class="f">Numéro de série</label>
          <input v-model="nouveau.numero_serie" class="inp" />
        </div>
        <div>
          <label class="f">Site</label>
          <select v-model="nouveau.site_id" class="inp">
            <option value="" disabled>Choisir…</option>
            <option v-for="s in parc.sites" :key="s.id" :value="s.id">{{ s.nom }}</option>
          </select>
          <label class="f">Emplacement</label>
          <input v-model="nouveau.emplacement" class="inp" />
          <label class="f">Date d'installation</label>
          <input v-model="nouveau.date_installation" type="date" class="inp" />
        </div>
      </div>
      <div v-if="erreurFormulaire" class="banner err" style="margin-top: 8px">{{ erreurFormulaire }}</div>
      <div style="display: flex; gap: 8px; margin-top: 10px">
        <button class="btn pri" style="width: auto" @click="soumettre">Enregistrer</button>
        <button class="btn gh" style="width: auto" @click="formulaireOuvert = false">Annuler</button>
      </div>
    </Modal>

    <div class="card">
      <table>
        <thead><tr><th>Identity</th><th>Marque / modèle</th><th>Site</th><th>Emplacement</th><th>Installé le</th><th>Statut</th><th v-if="peutGerer"></th></tr></thead>
        <tbody>
          <tr v-for="e in elementsPage" :key="e.id" style="cursor: pointer" @click="router.push({ name: 'parc-fiche', params: { id: e.id } })">
            <td><b>{{ e.identity }}</b></td>
            <td>{{ e.marque }} {{ e.modele }}</td>
            <td>{{ parc.nomSite(e.site_id) ?? `Site #${e.site_id}` }}</td>
            <td>{{ e.emplacement }}</td>
            <td>{{ formaterDateCivile(e.date_installation) }}</td>
            <td><span class="tag" :class="e.statut === 'en_service' ? 't-gr' : 't-or'">{{ e.statut }}</span></td>
            <td v-if="peutGerer" style="text-align: right">
              <button class="btn gh sm" style="width: auto" @click.stop="ouvrirEdition(e)">Modifier</button>
            </td>
          </tr>
          <tr v-if="!parc.chargement && !listeFiltree.length"><td :colspan="peutGerer ? 7 : 6" style="color: var(--mut)">Aucun équipement.</td></tr>
          <tr v-if="listeFiltree.length && !resultats.length"><td :colspan="peutGerer ? 7 : 6" style="color: var(--mut)">Aucun équipement ne correspond à la recherche.</td></tr>
        </tbody>
      </table>
      <BarrePagination :page="page" :total-pages="totalPages" @changer="allerPage">
        {{ resultats.length }} sur {{ parc.liste.length }} équipement{{ parc.liste.length > 1 ? "s" : "" }}
      </BarrePagination>
    </div>

    <Modal v-if="edition" titre="Corriger l'équipement" @fermer="edition = null">
      <div class="grid2">
        <div>
          <label class="f">Identity (SITE-FONCTION-NN)</label>
          <input v-model="champsEdition.identity" class="inp" />
          <label class="f">Marque</label>
          <select v-model="champsEdition.marque" class="inp"><option v-for="m in MARQUES" :key="m" :value="m">{{ m }}</option></select>
          <label class="f">Modèle</label>
          <input v-model="champsEdition.modele" class="inp" />
          <label class="f">Numéro de série</label>
          <input v-model="champsEdition.numero_serie" class="inp" />
        </div>
        <div>
          <label class="f">Site</label>
          <select v-model="champsEdition.site_id" class="inp">
            <option v-for="s in parc.sites" :key="s.id" :value="s.id">{{ s.nom }}</option>
          </select>
          <label class="f">Emplacement</label>
          <input v-model="champsEdition.emplacement" class="inp" />
          <label class="f">Date d'installation</label>
          <input v-model="champsEdition.date_installation" type="date" class="inp" />
        </div>
      </div>
      <div v-if="erreurEdition" class="banner err" style="margin-top: 8px">{{ erreurEdition }}</div>
      <div style="display: flex; gap: 8px; margin-top: 10px">
        <button class="btn pri" style="width: auto" @click="soumettreEdition">Enregistrer</button>
        <button class="btn gh" style="width: auto" @click="edition = null">Annuler</button>
      </div>
    </Modal>

    <Modal v-if="importOuvert" titre="Importer le parc" @fermer="importOuvert = false">
      <p style="font-size: 12.5px; color: var(--mut); margin-bottom: 8px">
        Fichier .csv ou .xlsx au format du gabarit d'inventaire (INV-SHEQ-001), 5 Mo maximum.
        Les colonnes non reconnues du gabarit réel sont acceptées mais ignorées.
      </p>
      <input type="file" accept=".csv,.xlsx" class="inp" @change="(e) => (fichierImport = e.target.files[0] ?? null)" />
      <div v-if="erreurImport" class="banner err" style="margin-top: 8px">{{ erreurImport }}</div>

      <div v-if="rapportImport" style="margin-top: 10px">
        <div class="banner" :class="rapportImport.en_erreur ? 'warn' : 'info'">
          {{ rapportImport.importees }} équipement{{ rapportImport.importees > 1 ? "s" : "" }} importé{{ rapportImport.importees > 1 ? "s" : "" }}
          sur {{ rapportImport.total_lignes }} ligne{{ rapportImport.total_lignes > 1 ? "s" : "" }}<template v-if="rapportImport.en_erreur"> — {{ rapportImport.en_erreur }} en erreur</template>.
        </div>
        <ul v-if="rapportImport.erreurs.length" class="cl" style="margin-top: 8px">
          <li v-for="err in rapportImport.erreurs" :key="err.ligne" class="ko">
            <span class="cb"><Icone nom="x" taille="sm" /></span>
            <span class="tx">Ligne {{ err.ligne }}{{ err.identity ? ` (${err.identity})` : "" }} — {{ err.erreurs.join(", ") }}</span>
          </li>
        </ul>
      </div>

      <div style="display: flex; gap: 8px; margin-top: 10px">
        <button class="btn pri" style="width: auto" :disabled="importEnCours" @click="soumettreImport">Importer</button>
        <button class="btn gh" style="width: auto" @click="importOuvert = false">Fermer</button>
      </div>
    </Modal>
  </div>
</template>

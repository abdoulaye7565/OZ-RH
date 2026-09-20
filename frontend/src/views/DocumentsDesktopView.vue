<script setup>
/**
 * Documents (SMI) — vue desktop (maquette #p-docs).
 *
 * Écart assumé, demandé explicitement par l'utilisateur : classement par
 * dossier réel du SMI (voir utils/dossiersDocuments.js pour la règle et sa
 * justification — identique à celle de l'écran mobile). Rendu ici en
 * filtres segmentés (`.seg`, déjà utilisé par Parc/Utilisateurs) plutôt
 * qu'en arborescence à ouvrir/fermer : cohérent avec le reste de
 * l'interface de gestion ("tableaux denses, filtres" — CDC 11.1), plus
 * adapté à un tableau qu'un navigateur de dossiers façon mobile.
 */
import { computed, onMounted, ref } from "vue";
import ApercuDocument from "../components/ApercuDocument.vue";
import BarrePagination from "../components/BarrePagination.vue";
import Icone from "../components/Icone.vue";
import Modal from "../components/Modal.vue";
import { useRechercheEtPagination } from "../composables/useRechercheEtPagination";
import { useAuthStore } from "../stores/auth";
import { useDocumentsStore } from "../stores/documents";
import { DOSSIERS, dossierDe } from "../utils/dossiersDocuments";

const auth = useAuthStore();
const documents = useDocumentsStore();
onMounted(() => documents.charger());

const peutGerer = computed(() => ["referent_sheq", "administrateur"].includes(auth.utilisateur?.role));
const peutApprouver = computed(() => ["responsable", "administrateur"].includes(auth.utilisateur?.role));

const STYLE_STATUT = {
  brouillon: "t-gy", en_approbation: "t-gd", en_vigueur: "t-gr", archive: "t-gy",
};

const dossierChoisi = ref("Tous");
const comptesParDossier = computed(() => {
  const comptes = {};
  for (const d of documents.liste) {
    const cle = dossierDe(d);
    comptes[cle] = (comptes[cle] ?? 0) + 1;
  }
  return comptes;
});
const listeFiltree = computed(() =>
  dossierChoisi.value === "Tous" ? documents.liste : documents.liste.filter((d) => dossierDe(d) === dossierChoisi.value)
);
const dossierActuel = computed(() => DOSSIERS.find((d) => d.cle === dossierChoisi.value));

function correspond(d, terme) {
  return d.reference?.toLowerCase().includes(terme) || d.intitule?.toLowerCase().includes(terme);
}
const { recherche, page, totalPages, resultats, elementsPage, allerPage } =
  useRechercheEtPagination(listeFiltree, correspond, 12);

const documentApercu = ref(null); // document actuellement prévisualisé, ou null
function ouvrirApercu(d) {
  documentApercu.value = d;
}

const formulaireOuvert = ref(false);
const nouveau = ref({ reference: "", intitule: "", niveau: 1, confidentialite: "normal" });
const fichier = ref(null);
const erreurFormulaire = ref(null);
function surFichierChange(e) {
  fichier.value = e.target.files[0] ?? null;
}
async function soumettre() {
  erreurFormulaire.value = null;
  try {
    await documents.creer({ ...nouveau.value, fichier: fichier.value });
    formulaireOuvert.value = false;
    nouveau.value = { reference: "", intitule: "", niveau: 1, confidentialite: "normal" };
    fichier.value = null;
  } catch (e) {
    erreurFormulaire.value = e?.message ?? "Impossible d'enregistrer ce document";
  }
}

// --- Correction des métadonnées d'un brouillon (2026-09-10). Refusé serveur
// au-delà du brouillon : au-delà, une nouvelle version est la voie normale. ---
const edition = ref(null);
const champsEdition = ref({ reference: "", intitule: "", niveau: 1, confidentialite: "normal" });
const erreurEdition = ref(null);

function ouvrirEdition(d) {
  edition.value = d;
  champsEdition.value = {
    reference: d.reference, intitule: d.intitule, niveau: d.niveau, confidentialite: d.confidentialite,
  };
  erreurEdition.value = null;
}
async function soumettreEdition() {
  erreurEdition.value = null;
  try {
    await documents.modifier(edition.value.id, champsEdition.value);
    edition.value = null;
  } catch (e) {
    erreurEdition.value = e?.message ?? "Impossible d'enregistrer la correction";
  }
}

// --- Nouvelle version d'un document en vigueur (2026-09-19) ---
const aReviser = ref(null);
const fichierNouvelleVersion = ref(null);
const erreurNouvelleVersion = ref(null);
function ouvrirNouvelleVersion(d) {
  aReviser.value = d;
  fichierNouvelleVersion.value = null;
  erreurNouvelleVersion.value = null;
}
async function soumettreNouvelleVersion() {
  erreurNouvelleVersion.value = null;
  try {
    await documents.nouvelleVersion(aReviser.value.id, fichierNouvelleVersion.value);
    aReviser.value = null;
  } catch (e) {
    erreurNouvelleVersion.value = e?.message ?? "Impossible de créer cette nouvelle version";
  }
}
</script>

<template>
  <div>
    <div v-if="documents.erreur" class="banner err">{{ documents.erreur }}</div>

    <div class="filters" style="flex-wrap: wrap">
      <button class="seg" :class="{ on: dossierChoisi === 'Tous' }" @click="dossierChoisi = 'Tous'">Tous · {{ documents.liste.length }}</button>
      <button
        v-for="d in DOSSIERS"
        :key="d.cle"
        class="seg"
        :class="{ on: dossierChoisi === d.cle }"
        :style="!comptesParDossier[d.cle] ? 'opacity:.5' : ''"
        @click="dossierChoisi = d.cle"
      >
        {{ d.abrege }} · {{ comptesParDossier[d.cle] ?? 0 }}
      </button>
      <span style="flex: 1"></span>
      <div class="srch">
        <Icone nom="search" taille="sm" />
        <input v-model="recherche" placeholder="Rechercher une référence, un intitulé…" />
      </div>
      <button v-if="peutGerer" class="btn pri sm" style="width: auto" @click="formulaireOuvert = true"><Icone nom="plus" taille="sm" />Nouveau document</button>
    </div>

    <div v-if="dossierActuel" class="banner info" style="margin-bottom: 12px">
      <Icone nom="doc" taille="sm" style="margin-top: 1px" />
      <div><b>{{ dossierActuel.nom }}</b> — {{ dossierActuel.description }}</div>
    </div>

    <Modal v-if="formulaireOuvert" titre="Nouveau document" @fermer="formulaireOuvert = false">
      <div class="grid2">
        <div>
          <label class="f">Référence</label><input v-model="nouveau.reference" class="inp" />
          <label class="f">Intitulé</label><input v-model="nouveau.intitule" class="inp" />
        </div>
        <div>
          <label class="f">Niveau (détermine le dossier)</label>
          <select v-model.number="nouveau.niveau" class="inp">
            <option :value="1">1 · Politique → 01-Politique_et_engagement</option>
            <option :value="2">2 · Pilotage → 02-Pilotage</option>
            <option :value="3">3 · Procédure → 03-Procedures_et_consignes</option>
            <option :value="4">4 · Formulaire → 04-Formulaires_vierges</option>
          </select>
          <label class="f">Confidentialité</label>
          <select v-model="nouveau.confidentialite" class="inp">
            <option value="normal">Normal</option>
            <option value="confidentiel">Confidentiel (→ .../CONFIDENTIEL)</option>
          </select>
          <label class="f">Fichier</label><input type="file" class="inp" @change="surFichierChange" />
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
        <thead><tr><th>Référence</th><th>Intitulé</th><th>Niveau</th><th>Version</th><th>Diffusion</th><th>Statut</th><th>Actions</th></tr></thead>
        <tbody>
          <tr v-for="d in elementsPage" :key="d.id">
            <td><b>{{ d.reference }}</b></td>
            <td>{{ d.intitule }}</td>
            <td>{{ d.niveau }}</td>
            <td>{{ d.version }}</td>
            <td>{{ d.accuses_lecture.length }} lecture{{ d.accuses_lecture.length > 1 ? "s" : "" }}</td>
            <td><span class="tag" :class="STYLE_STATUT[d.statut]">{{ d.statut }}</span></td>
            <td style="white-space: nowrap">
              <button v-if="d.statut === 'brouillon' && peutGerer" class="btn gh sm" style="width: auto" @click="ouvrirEdition(d)">Modifier</button>
              <button v-if="d.statut === 'brouillon' && peutGerer" class="btn gh sm" style="width: auto; margin-left: 6px" @click="documents.soumettreApprobation(d.id)">Soumettre</button>
              <button v-if="d.statut === 'en_approbation' && peutApprouver" class="btn gh sm" style="width: auto" @click="documents.approuver(d.id)">Approuver</button>
              <button v-if="d.statut === 'en_vigueur' && peutGerer" class="btn gh sm" style="width: auto" @click="ouvrirNouvelleVersion(d)">Nouvelle version</button>
              <button v-if="d.fichier" class="btn gh sm" style="width: auto; margin-left: 6px" @click="ouvrirApercu(d)">Aperçu</button>
            </td>
          </tr>
          <tr v-if="!documents.chargement && !listeFiltree.length"><td colspan="7" style="color: var(--mut)">Dossier vide.</td></tr>
          <tr v-if="listeFiltree.length && !resultats.length"><td colspan="7" style="color: var(--mut)">Aucun document ne correspond à la recherche.</td></tr>
        </tbody>
      </table>
      <BarrePagination :page="page" :total-pages="totalPages" @changer="allerPage">
        {{ resultats.length }} document{{ resultats.length > 1 ? "s" : "" }}
      </BarrePagination>
    </div>

    <ApercuDocument
      v-if="documentApercu"
      :document-id="documentApercu.id"
      :titre="`${documentApercu.reference} · ${documentApercu.intitule}`"
      :nom-fichier="documentApercu.fichier"
      @fermer="documentApercu = null"
    />

    <Modal v-if="edition" titre="Corriger le document" @fermer="edition = null">
      <label class="f">Référence</label><input v-model="champsEdition.reference" class="inp" />
      <label class="f">Intitulé</label><input v-model="champsEdition.intitule" class="inp" />
      <label class="f">Niveau (détermine le dossier)</label>
      <select v-model.number="champsEdition.niveau" class="inp">
        <option :value="1">1 · Politique → 01-Politique_et_engagement</option>
        <option :value="2">2 · Pilotage → 02-Pilotage</option>
        <option :value="3">3 · Procédure → 03-Procedures_et_consignes</option>
        <option :value="4">4 · Formulaire → 04-Formulaires_vierges</option>
      </select>
      <label class="f">Confidentialité</label>
      <select v-model="champsEdition.confidentialite" class="inp">
        <option value="normal">Normal</option>
        <option value="confidentiel">Confidentiel (→ .../CONFIDENTIEL)</option>
      </select>
      <div v-if="erreurEdition" class="banner err" style="margin: 8px 0">{{ erreurEdition }}</div>
      <div style="display: flex; gap: 8px; margin-top: 10px">
        <button class="btn pri" style="width: auto" @click="soumettreEdition">Enregistrer</button>
        <button class="btn gh" style="width: auto" @click="edition = null">Annuler</button>
      </div>
    </Modal>

    <Modal v-if="aReviser" titre="Nouvelle version" @fermer="aReviser = null">
      <p style="font-size: 12.5px; color: var(--mut); margin-bottom: 8px">
        Crée une nouvelle version de « {{ aReviser.reference }} » ({{ aReviser.intitule }}), qui repart en brouillon.
        La version {{ aReviser.version }} actuellement en vigueur reste consultable telle quelle.
      </p>
      <label class="f">Nouveau fichier (facultatif — reprend l'actuel si omis)</label>
      <input type="file" class="inp" @change="(e) => (fichierNouvelleVersion = e.target.files[0] ?? null)" />
      <div v-if="erreurNouvelleVersion" class="banner err" style="margin-top: 8px">{{ erreurNouvelleVersion }}</div>
      <div style="display: flex; gap: 8px; margin-top: 10px">
        <button class="btn pri" style="width: auto" @click="soumettreNouvelleVersion">Créer la nouvelle version</button>
        <button class="btn gh" style="width: auto" @click="aReviser = null">Annuler</button>
      </div>
    </Modal>
  </div>
</template>

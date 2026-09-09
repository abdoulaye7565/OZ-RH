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
import Icone from "../components/Icone.vue";
import api from "../services/api";
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

async function ouvrirFichier(id) {
  try {
    const reponse = await api.requete(`/api/v1/documents/${id}/fichier`, { brut: true });
    const blob = await reponse.blob();
    window.open(URL.createObjectURL(blob), "_blank");
  } catch {
    // Aucun fichier, ou droits insuffisants.
  }
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
      <button v-if="peutGerer" class="btn pri sm" style="width: auto" @click="formulaireOuvert = !formulaireOuvert"><Icone nom="plus" taille="sm" />Nouveau document</button>
    </div>

    <div v-if="dossierActuel" class="banner info" style="margin-bottom: 12px">
      <Icone nom="doc" taille="sm" style="margin-top: 1px" />
      <div><b>{{ dossierActuel.nom }}</b> — {{ dossierActuel.description }}</div>
    </div>

    <div v-if="formulaireOuvert" class="card">
      <div class="ch"><h3>Nouveau document</h3></div>
      <div class="cb">
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
        <button class="btn pri" style="width: auto; margin-top: 10px" @click="soumettre">Enregistrer</button>
      </div>
    </div>

    <div class="card">
      <table>
        <thead><tr><th>Référence</th><th>Intitulé</th><th>Niveau</th><th>Version</th><th>Diffusion</th><th>Statut</th><th>Actions</th></tr></thead>
        <tbody>
          <tr v-for="d in listeFiltree" :key="d.id">
            <td><b>{{ d.reference }}</b></td>
            <td>{{ d.intitule }}</td>
            <td>{{ d.niveau }}</td>
            <td>{{ d.version }}</td>
            <td>{{ d.accuses_lecture.length }} lecture{{ d.accuses_lecture.length > 1 ? "s" : "" }}</td>
            <td><span class="tag" :class="STYLE_STATUT[d.statut]">{{ d.statut }}</span></td>
            <td>
              <button v-if="d.statut === 'brouillon' && peutGerer" class="btn gh sm" style="width: auto" @click="documents.soumettreApprobation(d.id)">Soumettre</button>
              <button v-if="d.statut === 'en_approbation' && peutApprouver" class="btn gh sm" style="width: auto" @click="documents.approuver(d.id)">Approuver</button>
              <button v-if="d.fichier" class="btn gh sm" style="width: auto" @click="ouvrirFichier(d.id)">Ouvrir</button>
            </td>
          </tr>
          <tr v-if="!documents.chargement && !listeFiltree.length"><td colspan="7" style="color: var(--mut)">Dossier vide.</td></tr>
        </tbody>
      </table>
      <div class="pagin"><span>{{ listeFiltree.length }} document{{ listeFiltree.length > 1 ? "s" : "" }}</span></div>
    </div>
  </div>
</template>

<script setup>
/**
 * Documents (SMI) — vue mobile, écran de dossiers (maquette #s-docs, adaptée).
 *
 * Écart assumé, demandé explicitement par l'utilisateur après avoir vu le
 * premier écran (liste plate) : "le module Document doit avoir des sous
 * dossier comme dans le SMI et chaque fichier serait dans son dossier".
 * La maquette #s-docs elle-même ne montre qu'une liste plate — ce classement
 * en dossiers n'y a pas de référence visuelle, construit pour refléter la
 * vraie arborescence du classeur (`SMI-SHEQ_Hirondelles_IT_Lab/LISEZ-MOI.txt`)
 * plutôt qu'un simple filtre inventé. Voir dossierDe() (utils/dossiersDocuments.js)
 * pour la règle de classement (dérivée de niveau/confidentialité/statut,
 * pas un nouveau champ en base).
 */
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import Icone from "../components/Icone.vue";
import BandeauReseau from "../components/BandeauReseau.vue";
import { useAuthStore } from "../stores/auth";
import { useDocumentsStore } from "../stores/documents";
import { DOSSIERS, dossierDe } from "../utils/dossiersDocuments";

const router = useRouter();
const auth = useAuthStore();
const documents = useDocumentsStore();
onMounted(() => documents.charger());

const peutGerer = computed(() => ["referent_sheq", "administrateur"].includes(auth.utilisateur?.role));

const comptesParDossier = computed(() => {
  const comptes = {};
  for (const d of documents.liste) {
    const cle = dossierDe(d);
    comptes[cle] = (comptes[cle] ?? 0) + 1;
  }
  return comptes;
});

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
  <div class="ecran-mobile">
    <BandeauReseau />
    <header class="hd">
      <button class="back" aria-label="Retour" @click="router.push({ name: 'menu' })"><Icone nom="back" /></button>
      <div>
        <h1>Documents</h1>
        <div class="sub">{{ documents.liste.length }} référencés · liste maîtresse</div>
      </div>
    </header>

    <div class="wrap">
      <div class="body">
        <div class="pad">
          <div v-if="documents.erreur" class="banner err">{{ documents.erreur }}</div>
          <div v-else-if="documents.chargement" class="skel" style="height: 64px"></div>

          <div
            v-for="d in DOSSIERS"
            :key="d.cle"
            class="row"
            role="button"
            tabindex="0"
            @click="router.push({ name: 'documents-dossier', params: { dossier: d.cle } })"
            @keydown.enter="router.push({ name: 'documents-dossier', params: { dossier: d.cle } })"
          >
            <span class="lead" :class="comptesParDossier[d.cle] ? 'nv' : 'gy'"><Icone nom="doc" /></span>
            <div class="tx">
              <b>{{ d.nom }}</b>
              <div class="meta"><span>{{ d.description }}</span></div>
            </div>
            <span class="tag" :class="comptesParDossier[d.cle] ? 't-bl' : 't-gy'">{{ comptesParDossier[d.cle] ?? 0 }}</span>
          </div>

          <div v-if="peutGerer">
            <div v-if="!formulaireOuvert" style="height: 12px"></div>
            <button v-if="!formulaireOuvert" class="btn pri" @click="formulaireOuvert = true"><Icone nom="plus" taille="sm" />Nouveau document</button>
            <div v-if="formulaireOuvert" class="card" style="padding: 13px; margin-top: 4px">
              <div class="sec" style="margin-bottom: 8px">NOUVEAU DOCUMENT</div>
              <label class="f">Référence</label>
              <input v-model="nouveau.reference" class="inp" placeholder="Ex. PRO-SHEQ-010" />
              <label class="f">Intitulé</label>
              <input v-model="nouveau.intitule" class="inp" />
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
              <label class="f">Fichier (facultatif)</label>
              <input type="file" class="inp" @change="surFichierChange" />
              <div v-if="erreurFormulaire" class="banner err" style="margin-top: 8px">{{ erreurFormulaire }}</div>
              <div class="btnrow" style="margin-top: 10px">
                <button class="btn pri sm" style="width: auto" @click="soumettre">Enregistrer</button>
                <button class="btn gh sm" style="width: auto" @click="formulaireOuvert = false">Annuler</button>
              </div>
            </div>
          </div>

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

<script setup>
/**
 * Audits internes & revues de direction — vue mobile (maquette #s-audit).
 *
 * Écart assumé : maquette et sidebar regroupent "Audits & revues" en un seul
 * module — un seul écran ici aussi, en deux sections, plutôt que deux écrans
 * séparés qui dupliqueraient une bonne partie de la structure.
 */
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import Icone from "../components/Icone.vue";
import BandeauReseau from "../components/BandeauReseau.vue";
import { useAuditsStore } from "../stores/audits";

const router = useRouter();
const audits = useAuditsStore();
onMounted(() => audits.charger());

const exigencesParChapitre = computed(() => {
  const groupes = {};
  for (const e of audits.exigences) {
    groupes[e.chapitre] ??= [];
    groupes[e.chapitre].push(e);
  }
  return groupes;
});

function cotationDe(exigenceId) {
  return audits.campagne?.cotations?.find((c) => c.exigence_id === exigenceId)?.cotation ?? null;
}

async function coter(exigenceId, valeur) {
  await audits.coter(exigenceId, valeur);
}

// --- Revue de direction ---
const revueOuverte = ref(false);
const nouvelleRevue = ref({ date: "", lieu: "", periode_debut: "", periode_fin: "", participants: "" });
const revueCreee = ref(null);
const erreurRevue = ref(null);

async function soumettreRevue() {
  erreurRevue.value = null;
  try {
    revueCreee.value = await audits.creerRevue(nouvelleRevue.value);
  } catch (e) {
    erreurRevue.value = e?.message ?? "Impossible d'enregistrer la revue";
  }
}

const nouvelleDecision = ref({ libelle: "", responsable_id: "", echeance: "" });
async function ajouterDecision() {
  await audits.ajouterDecision(revueCreee.value.id, {
    libelle: nouvelleDecision.value.libelle,
    responsable_id: Number(nouvelleDecision.value.responsable_id),
    echeance: nouvelleDecision.value.echeance,
  });
  nouvelleDecision.value = { libelle: "", responsable_id: "", echeance: "" };
}
</script>

<template>
  <div class="ecran-mobile">
    <BandeauReseau />
    <header class="hd">
      <button class="back" aria-label="Retour" @click="router.push({ name: 'menu' })"><Icone nom="back" /></button>
      <div>
        <h1>Audits &amp; revues</h1>
        <div class="sub">Base ISO 45001 · 0 / 1 / 2</div>
      </div>
    </header>

    <div class="wrap">
      <div class="body">
        <div class="pad">
          <div v-if="audits.erreur" class="banner err">{{ audits.erreur }}</div>

          <div class="sec">AUDIT INTERNE</div>
          <button v-if="!audits.campagne" class="btn pri" @click="audits.ouvrirCampagne">Ouvrir une campagne d'audit</button>

          <template v-else>
            <div class="statbar">
              <span>Maturité du système</span>
              <span class="v">{{ audits.campagne.taux_conformite_pourcent?.toFixed(0) ?? "—" }} % — {{ audits.campagne.interpretation }}</span>
            </div>
            <template v-for="(exigences, chapitre) in exigencesParChapitre" :key="chapitre">
              <div class="sec" style="margin-top: 10px">{{ chapitre }}</div>
              <ul class="cl">
                <li v-for="e in exigences" :key="e.id">
                  <span class="tx">{{ e.libelle }}</span>
                  <span class="tri">
                    <button class="n" :class="{ on: cotationDe(e.id) === 0 }" @click="coter(e.id, 0)">0</button>
                    <button class="s" :class="{ on: cotationDe(e.id) === 1 }" @click="coter(e.id, 1)">1</button>
                    <button class="c" :class="{ on: cotationDe(e.id) === 2 }" @click="coter(e.id, 2)">2</button>
                  </span>
                </li>
              </ul>
            </template>
            <button v-if="audits.campagne.statut !== 'cloturee'" class="btn pri" style="margin-top: 10px" @click="audits.cloturerCampagne">
              Clôturer et générer le rapport
            </button>
            <p v-else style="font-size: 12px; color: var(--green); font-weight: 650">Campagne clôturée.</p>
          </template>

          <div class="sec" style="margin-top: 18px">REVUE DE DIRECTION</div>
          <button v-if="!revueOuverte && !revueCreee" class="btn gh" @click="revueOuverte = true">Nouvelle revue de direction</button>

          <div v-if="revueOuverte && !revueCreee" class="card" style="padding: 13px">
            <label class="f">Date</label>
            <input v-model="nouvelleRevue.date" type="date" class="inp" />
            <label class="f">Lieu</label>
            <input v-model="nouvelleRevue.lieu" class="inp" />
            <label class="f">Période — début</label>
            <input v-model="nouvelleRevue.periode_debut" type="date" class="inp" />
            <label class="f">Période — fin</label>
            <input v-model="nouvelleRevue.periode_fin" type="date" class="inp" />
            <label class="f">Participants</label>
            <input v-model="nouvelleRevue.participants" class="inp" placeholder="Direction, référent SHEQ…" />
            <div v-if="erreurRevue" class="banner err" style="margin-top: 8px">{{ erreurRevue }}</div>
            <button class="btn pri sm" style="width: auto; margin-top: 10px" @click="soumettreRevue">Enregistrer</button>
          </div>

          <template v-if="revueCreee">
            <div class="banner info">Revue {{ revueCreee.reference ?? "créée" }} enregistrée. Ajoutez les décisions ci-dessous.</div>
            <div class="card" style="padding: 13px; margin-top: 8px">
              <label class="f">Décision</label>
              <input v-model="nouvelleDecision.libelle" class="inp" />
              <label class="f">Responsable</label>
              <select v-model="nouvelleDecision.responsable_id" class="inp">
                <option value="" disabled>Choisir…</option>
                <option v-for="u in audits.utilisateurs" :key="u.id" :value="u.id">{{ u.prenom }} {{ u.nom }}</option>
              </select>
              <label class="f">Échéance</label>
              <input v-model="nouvelleDecision.echeance" type="date" class="inp" />
              <button class="btn pri sm" style="width: auto; margin-top: 10px" @click="ajouterDecision">Ajouter la décision</button>
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
      <button class="tb" @click="router.push({ name: 'tableau-de-bord' })"><Icone nom="chart" />Tableau</button>
      <button class="tb" @click="router.push({ name: 'menu' })"><Icone nom="grid" />Menu</button>
    </nav>
  </div>
</template>

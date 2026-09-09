<script setup>
/**
 * Audits internes & revues de direction — vue desktop (maquette #p-audit /
 * #p-revue, regroupées comme dans la barre latérale).
 */
import { computed, onMounted, ref } from "vue";
import Icone from "../components/Icone.vue";
import { useAuditsStore } from "../stores/audits";

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
    libelle: nouvelleDecision.value.libelle, responsable_id: Number(nouvelleDecision.value.responsable_id), echeance: nouvelleDecision.value.echeance,
  });
  nouvelleDecision.value = { libelle: "", responsable_id: "", echeance: "" };
}
</script>

<template>
  <div>
    <div v-if="audits.erreur" class="banner err">{{ audits.erreur }}</div>

    <div class="card">
      <div class="ch"><Icone nom="list" /><h3>Audit interne</h3>
        <span v-if="!audits.campagne" class="r" @click="audits.ouvrirCampagne">Ouvrir une campagne</span>
      </div>
      <div class="cb" v-if="audits.campagne">
        <div class="statbar" style="margin-bottom: 12px">
          <span>Maturité du système</span>
          <span class="v">{{ audits.campagne.taux_conformite_pourcent?.toFixed(0) ?? "—" }} % — {{ audits.campagne.interpretation }}</span>
        </div>
        <template v-for="(exigences, chapitre) in exigencesParChapitre" :key="chapitre">
          <div class="sec" style="margin: 10px 0 6px">{{ chapitre }}</div>
          <ul class="cl">
            <li v-for="e in exigences" :key="e.id">
              <span class="tx">{{ e.libelle }}</span>
              <span class="tri">
                <button class="n" :class="{ on: cotationDe(e.id) === 0 }" @click="audits.coter(e.id, 0)">0</button>
                <button class="s" :class="{ on: cotationDe(e.id) === 1 }" @click="audits.coter(e.id, 1)">1</button>
                <button class="c" :class="{ on: cotationDe(e.id) === 2 }" @click="audits.coter(e.id, 2)">2</button>
              </span>
            </li>
          </ul>
        </template>
        <button v-if="audits.campagne.statut !== 'cloturee'" class="btn pri" style="width: auto; margin-top: 10px" @click="audits.cloturerCampagne">
          Clôturer et générer le rapport
        </button>
      </div>
    </div>

    <div class="card">
      <div class="ch"><Icone nom="check" /><h3>Revue de direction</h3>
        <span v-if="!revueOuverte && !revueCreee" class="r" @click="revueOuverte = true">Nouvelle revue</span>
      </div>
      <div class="cb" v-if="revueOuverte && !revueCreee">
        <div class="grid2">
          <div>
            <label class="f">Date</label><input v-model="nouvelleRevue.date" type="date" class="inp" />
            <label class="f">Lieu</label><input v-model="nouvelleRevue.lieu" class="inp" />
          </div>
          <div>
            <label class="f">Période — début</label><input v-model="nouvelleRevue.periode_debut" type="date" class="inp" />
            <label class="f">Période — fin</label><input v-model="nouvelleRevue.periode_fin" type="date" class="inp" />
          </div>
        </div>
        <label class="f">Participants</label><input v-model="nouvelleRevue.participants" class="inp" />
        <div v-if="erreurRevue" class="banner err" style="margin-top: 8px">{{ erreurRevue }}</div>
        <button class="btn pri" style="width: auto; margin-top: 10px" @click="soumettreRevue">Enregistrer</button>
      </div>
      <div class="cb" v-if="revueCreee">
        <div class="banner info" style="margin-bottom: 10px">Revue {{ revueCreee.reference ?? "créée" }} enregistrée. Ajoutez les décisions ci-dessous.</div>
        <div class="grid2">
          <input v-model="nouvelleDecision.libelle" class="inp" placeholder="Décision" />
          <select v-model="nouvelleDecision.responsable_id" class="inp">
            <option value="" disabled>Responsable…</option>
            <option v-for="u in audits.utilisateurs" :key="u.id" :value="u.id">{{ u.prenom }} {{ u.nom }}</option>
          </select>
        </div>
        <input v-model="nouvelleDecision.echeance" type="date" class="inp" style="margin-top: 8px" />
        <button class="btn pri" style="width: auto; margin-top: 10px" @click="ajouterDecision">Ajouter la décision</button>
      </div>
    </div>
  </div>
</template>

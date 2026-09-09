<script setup>
/**
 * Plan d'action — vue desktop (maquette #p-act). Écart : "Origine" affiche
 * simplement "Risque" (pas de résolution du numéro de risque depuis
 * risque_id sans appel supplémentaire par ligne) ; pas de pagination.
 */
import { computed, onMounted, ref } from "vue";
import Icone from "../components/Icone.vue";
import { useActionsStore } from "../stores/actions";
import { formaterDateCivile } from "../utils/dates";

const actions = useActionsStore();
onMounted(() => actions.charger());

const filtre = ref("toutes");
const listeFiltree = computed(() => {
  if (filtre.value === "retard") return actions.liste.filter((a) => a.en_retard);
  if (filtre.value === "cours") return actions.liste.filter((a) => a.statut === "en_cours" && !a.en_retard);
  if (filtre.value === "realisees") return actions.liste.filter((a) => a.statut === "cloturee");
  return actions.liste;
});
const nombreEnRetard = computed(() => actions.liste.filter((a) => a.en_retard).length);
const nombreEnCours = computed(() => actions.liste.filter((a) => a.statut === "en_cours" && !a.en_retard).length);
const nombreRealisees = computed(() => actions.liste.filter((a) => a.statut === "cloturee").length);

function etat(a) {
  if (a.statut === "cloturee") return { tag: "t-gr", libelle: "Réalisée", barre: "g" };
  if (a.en_retard) return { tag: "t-red", libelle: "En retard", barre: "o" };
  return { tag: "t-gd", libelle: "En cours", barre: "gd" };
}
function origine(a) {
  if (a.risque_id) return `Risque #${a.risque_id}`;
  if (a.signalement_id) return `Signalement #${a.signalement_id}`;
  if (a.inspection_id) return `Inspection #${a.inspection_id}`;
  if (a.cotation_audit_id) return "Écart d'audit";
  if (a.reponse_satisfaction_id) return "Satisfaction";
  return "—";
}
const formaterDate = formaterDateCivile;

const formulaireOuvert = ref(false);
const nouvelle = ref({ libelle: "", risque_id: "", type_mesure: "corrective", responsable_id: "", echeance: "" });
const erreurFormulaire = ref(null);

async function soumettre() {
  erreurFormulaire.value = null;
  try {
    await actions.creer({
      libelle: nouvelle.value.libelle, risque_id: Number(nouvelle.value.risque_id),
      type_mesure: nouvelle.value.type_mesure, responsable_id: Number(nouvelle.value.responsable_id),
      echeance: nouvelle.value.echeance,
    });
    formulaireOuvert.value = false;
    nouvelle.value = { libelle: "", risque_id: "", type_mesure: "corrective", responsable_id: "", echeance: "" };
  } catch (e) {
    erreurFormulaire.value = e?.message ?? "Impossible d'enregistrer cette action";
  }
}
</script>

<template>
  <div>
    <div v-if="actions.erreur" class="banner err">{{ actions.erreur }}</div>

    <div class="filters">
      <button class="seg" :class="{ on: filtre === 'toutes' }" @click="filtre = 'toutes'">Toutes · {{ actions.liste.length }}</button>
      <button class="seg" :class="{ on: filtre === 'retard' }" @click="filtre = 'retard'">En retard · {{ nombreEnRetard }}</button>
      <button class="seg" :class="{ on: filtre === 'cours' }" @click="filtre = 'cours'">En cours · {{ nombreEnCours }}</button>
      <button class="seg" :class="{ on: filtre === 'realisees' }" @click="filtre = 'realisees'">Réalisées · {{ nombreRealisees }}</button>
      <span style="flex: 1"></span>
      <button class="btn pri sm" style="width: auto" @click="formulaireOuvert = !formulaireOuvert"><Icone nom="plus" taille="sm" />Nouvelle action</button>
    </div>

    <div v-if="formulaireOuvert" class="card">
      <div class="ch"><h3>Nouvelle action (à partir d'un risque)</h3></div>
      <div class="cb">
        <div class="grid2">
          <div>
            <label class="f">Libellé</label>
            <input v-model="nouvelle.libelle" class="inp" />
            <label class="f">Risque d'origine</label>
            <select v-model="nouvelle.risque_id" class="inp">
              <option value="" disabled>Choisir…</option>
              <option v-for="r in actions.risques" :key="r.id" :value="r.id">{{ r.danger }}</option>
            </select>
          </div>
          <div>
            <label class="f">Type de mesure</label>
            <select v-model="nouvelle.type_mesure" class="inp">
              <option value="corrective">Corrective</option><option value="preventive">Préventive</option><option value="amelioration">Amélioration</option>
            </select>
            <label class="f">Responsable</label>
            <select v-model="nouvelle.responsable_id" class="inp">
              <option value="" disabled>Choisir…</option>
              <option v-for="u in actions.utilisateurs" :key="u.id" :value="u.id">{{ u.prenom }} {{ u.nom }}</option>
            </select>
            <label class="f">Échéance</label>
            <input v-model="nouvelle.echeance" type="date" class="inp" />
          </div>
        </div>
        <div v-if="erreurFormulaire" class="banner err" style="margin-top: 8px">{{ erreurFormulaire }}</div>
        <button class="btn pri" style="width: auto; margin-top: 10px" @click="soumettre">Enregistrer</button>
      </div>
    </div>

    <div class="card">
      <table>
        <thead><tr><th>Action</th><th>Origine</th><th>Responsable</th><th>Échéance</th><th style="width: 130px">Avancement</th><th>Statut</th></tr></thead>
        <tbody>
          <tr v-for="a in listeFiltree" :key="a.id">
            <td><b>{{ a.libelle }}</b></td>
            <td><span class="tag t-gy">{{ origine(a) }}</span></td>
            <td>{{ actions.nomUtilisateur(a.responsable_id) ?? `Utilisateur #${a.responsable_id}` }}</td>
            <td>
              <b :style="a.en_retard ? 'color:var(--red)' : ''">{{ formaterDate(a.echeance) }}</b>
              <div class="sub" v-if="a.en_retard" style="color: var(--red)">En retard</div>
            </td>
            <td><div class="trk"><div class="fl" :class="etat(a).barre" :style="{ width: a.avancement + '%' }"></div></div><div class="sub">{{ a.avancement }} %</div></td>
            <td><span class="tag" :class="etat(a).tag">{{ etat(a).libelle }}</span></td>
          </tr>
          <tr v-if="!actions.chargement && !listeFiltree.length"><td colspan="6" style="color: var(--mut)">Aucune action.</td></tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

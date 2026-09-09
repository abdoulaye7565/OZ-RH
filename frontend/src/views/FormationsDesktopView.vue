<script setup>
/**
 * Formations — vue desktop (maquette #p-form). Écart : le passage de quiz
 * n'est proposé que côté mobile (FormationsView.vue) — une action
 * individuelle, pas une vue de pilotage.
 */
import { onMounted, ref } from "vue";
import Icone from "../components/Icone.vue";
import api from "../services/api";
import { useFormationsStore } from "../stores/formations";
import { formaterDateCivile } from "../utils/dates";

const formations = useFormationsStore();
const matrice = ref([]);

onMounted(async () => {
  await formations.charger();
  try {
    matrice.value = await api.requete("/api/v1/formations/matrice");
  } catch {
    // Réservé à un rôle de vue d'ensemble (référent SHEQ/responsable/admin) —
    // un rôle sans ce droit voit simplement une matrice vide plutôt qu'une erreur bloquante.
  }
});

function nomUtilisateur(id) {
  return formations.nomUtilisateur(id) ?? `Utilisateur #${id}`;
}

const formulaireOuvert = ref(false);
const nouvelle = ref({ theme: "", date: "", lieu: "", animateur_id: "", competence_id: "" });
const erreurFormulaire = ref(null);

async function soumettre() {
  erreurFormulaire.value = null;
  try {
    await formations.creerSeance({
      theme: nouvelle.value.theme, date: nouvelle.value.date, lieu: nouvelle.value.lieu,
      animateur_id: Number(nouvelle.value.animateur_id),
      competence_id: nouvelle.value.competence_id ? Number(nouvelle.value.competence_id) : null,
    });
    formulaireOuvert.value = false;
    nouvelle.value = { theme: "", date: "", lieu: "", animateur_id: "", competence_id: "" };
  } catch (e) {
    erreurFormulaire.value = e?.message ?? "Impossible d'enregistrer cette séance";
  }
}
</script>

<template>
  <div>
    <div v-if="formations.erreur" class="banner err">{{ formations.erreur }}</div>

    <div class="grid2" style="grid-template-columns: 1fr 1fr">
      <div class="card">
        <div class="ch"><Icone nom="cap" /><h3>Séances</h3><span class="r" @click="formulaireOuvert = !formulaireOuvert">Nouvelle séance</span></div>
        <div class="cb">
          <div v-if="formulaireOuvert" style="margin-bottom: 12px">
            <label class="f">Thème</label><input v-model="nouvelle.theme" class="inp" />
            <label class="f">Date</label><input v-model="nouvelle.date" type="date" class="inp" />
            <label class="f">Lieu</label><input v-model="nouvelle.lieu" class="inp" />
            <label class="f">Animateur</label>
            <select v-model="nouvelle.animateur_id" class="inp">
              <option value="" disabled>Choisir…</option>
              <option v-for="u in formations.utilisateurs" :key="u.id" :value="u.id">{{ u.prenom }} {{ u.nom }}</option>
            </select>
            <div v-if="erreurFormulaire" class="banner err" style="margin-top: 8px">{{ erreurFormulaire }}</div>
            <button class="btn pri" style="width: auto; margin-top: 8px" @click="soumettre">Enregistrer</button>
          </div>
          <div v-for="s in formations.seances" :key="s.id" class="kv">
            <span>{{ s.theme }} — {{ formaterDateCivile(s.date) }}</span>
            <b>{{ s.statut }}</b>
          </div>
          <p v-if="!formations.seances.length" style="color: var(--mut); font-size: 12.5px">Aucune séance planifiée.</p>
        </div>
      </div>
      <div class="card">
        <div class="ch"><Icone nom="check" /><h3>Compétences</h3></div>
        <div class="cb">
          <div v-for="c in formations.competences" :key="c.id" class="kv">
            <span>{{ c.libelle }}</span><b>Recyclage {{ c.periodicite_mois }} mois</b>
          </div>
          <p v-if="!formations.competences.length" style="color: var(--mut); font-size: 12.5px">Aucune compétence enregistrée.</p>
        </div>
      </div>
    </div>

    <div class="card">
      <div class="ch"><h3>Matrice de compétences</h3></div>
      <table>
        <thead><tr><th>Collaborateur</th><th>Compétence</th><th>Obtenue le</th><th>Expire le</th><th>Statut</th></tr></thead>
        <tbody>
          <tr v-for="(l, i) in matrice" :key="i">
            <td><b>{{ nomUtilisateur(l.utilisateur_id) }}</b></td>
            <td>{{ l.libelle_competence }}</td>
            <td>{{ formaterDateCivile(l.date_obtention) }}</td>
            <td>{{ formaterDateCivile(l.date_expiration) }}</td>
            <td><span class="tag" :class="l.expiree ? 't-or' : 't-gr'">{{ l.expiree ? "À renouveler" : "Valide" }}</span></td>
          </tr>
          <tr v-if="!matrice.length"><td colspan="5" style="color: var(--mut)">Aucune habilitation enregistrée.</td></tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

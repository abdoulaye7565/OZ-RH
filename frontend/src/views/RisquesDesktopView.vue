<script setup>
/**
 * Registre des risques — vue desktop (maquette #p-risk).
 *
 * Écart assumé : pas de colonne "Actions liées" (nécessiterait une jointure
 * non exposée par l'API actuelle) ; la formulaire d'ajout est repris de
 * RisquesView.vue plutôt que dupliqué avec un style desktop distinct.
 */
import { computed, onMounted, ref } from "vue";
import Icone from "../components/Icone.vue";
import { useRisquesStore } from "../stores/risques";

const risques = useRisquesStore();
onMounted(() => risques.charger());

const CATEGORIES = [
  "Ergonomique", "Électrique", "Incendie", "Chute / Circulation", "Psychosocial (RPS)",
  "Manutention", "Ambiances physiques", "Hygiène / Biologique", "Sécurité de l'information",
  "Sécurité / Sûreté", "Routier / Trajet", "Incendie / Urgences",
];
const TAG_NIVEAU = { faible: "t-gr", modéré: "t-gd", élevé: "t-or", critique: "t-red" };

function celluleMatrice(probabilite, gravite) {
  return risques.matrice.find((c) => c.probabilite === probabilite && c.gravite === gravite);
}

const total = computed(() => risques.liste.length);
const parNiveau = computed(() => {
  const compte = { critique: 0, élevé: 0, modéré: 0, faible: 0 };
  for (const r of risques.liste) {
    const n = r.derniere_cotation?.niveau;
    if (n && n in compte) compte[n]++;
  }
  return compte;
});
function pourcent(n) {
  return total.value ? Math.round((n / total.value) * 100) : 0;
}

const listeTriee = computed(() =>
  [...risques.liste].sort((a, b) => (b.derniere_cotation?.criticite ?? 0) - (a.derniere_cotation?.criticite ?? 0))
);

const formulaireOuvert = ref(false);
const nouveau = ref({ danger: "", categorie: CATEGORIES[0], unite_travail: "", probabilite: 3, gravite: 3, mesures_proposees: "" });
const erreurFormulaire = ref(null);

async function soumettre() {
  erreurFormulaire.value = null;
  try {
    await risques.creer({
      danger: nouveau.value.danger,
      categorie: nouveau.value.categorie,
      unite_travail: nouveau.value.unite_travail,
      cotation: { probabilite: Number(nouveau.value.probabilite), gravite: Number(nouveau.value.gravite), mesures_proposees: nouveau.value.mesures_proposees },
    });
    formulaireOuvert.value = false;
    nouveau.value = { danger: "", categorie: CATEGORIES[0], unite_travail: "", probabilite: 3, gravite: 3, mesures_proposees: "" };
  } catch (e) {
    erreurFormulaire.value = e?.message ?? "Impossible d'enregistrer ce risque";
  }
}
</script>

<template>
  <div>
    <div style="display: flex; margin-bottom: 14px">
      <button class="btn pri" style="width: auto; margin-left: auto" @click="formulaireOuvert = !formulaireOuvert">
        <Icone nom="plus" taille="sm" />Ajouter un risque
      </button>
    </div>

    <div v-if="risques.erreur" class="banner err">{{ risques.erreur }}</div>

    <div v-if="formulaireOuvert" class="card">
      <div class="ch"><h3>Nouveau risque</h3></div>
      <div class="cb">
        <div class="grid2">
          <div>
            <label class="f">Danger</label>
            <input v-model="nouveau.danger" class="inp" />
            <label class="f">Catégorie</label>
            <select v-model="nouveau.categorie" class="inp"><option v-for="c in CATEGORIES" :key="c" :value="c">{{ c }}</option></select>
            <label class="f">Unité de travail</label>
            <input v-model="nouveau.unite_travail" class="inp" />
          </div>
          <div>
            <div style="display: flex; gap: 7px">
              <div style="flex: 1"><label class="f">Probabilité</label><select v-model="nouveau.probabilite" class="inp"><option v-for="n in [1, 2, 3, 4, 5]" :key="n" :value="n">{{ n }}</option></select></div>
              <div style="flex: 1"><label class="f">Gravité</label><select v-model="nouveau.gravite" class="inp"><option v-for="n in [1, 2, 3, 4, 5]" :key="n" :value="n">{{ n }}</option></select></div>
            </div>
            <label class="f">Mesures proposées</label>
            <textarea v-model="nouveau.mesures_proposees" class="inp"></textarea>
          </div>
        </div>
        <div v-if="erreurFormulaire" class="banner err" style="margin-top: 8px">{{ erreurFormulaire }}</div>
        <button class="btn pri" style="width: auto; margin-top: 10px" @click="soumettre">Enregistrer</button>
      </div>
    </div>

    <div class="grid2" style="grid-template-columns: 1fr 1fr">
      <div class="card">
        <div class="ch"><Icone nom="target" /><h3>Matrice de criticité</h3><span class="r">{{ total }} risques positionnés</span></div>
        <div class="cb">
          <div class="mtx">
            <template v-for="p in [5, 4, 3, 2, 1]" :key="p">
              <span class="ax">{{ p }}</span>
              <span v-for="g in [1, 2, 3, 4, 5]" :key="g" class="tag" :class="TAG_NIVEAU[celluleMatrice(p, g)?.niveau] ?? 't-gy'" style="justify-content: center; padding: 6px 0">
                {{ celluleMatrice(p, g)?.risques?.length || "" }}
              </span>
            </template>
          </div>
          <div style="display: flex; justify-content: space-between; font-size: 10.5px; color: var(--mut); margin-top: 8px">
            <span>Probabilité ↑ · Gravité →</span>
          </div>
        </div>
      </div>
      <div class="card">
        <div class="ch"><Icone nom="chart" /><h3>Répartition par niveau</h3></div>
        <div class="cb">
          <div v-for="(libelle, cle) in { critique: 'Critique (C ≥ 15)', élevé: 'Élevé (8–14)', modéré: 'Modéré (4–7)', faible: 'Faible (< 4)' }" :key="cle" style="margin-bottom: 12px">
            <div style="display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 5px"><b>{{ libelle }}</b><span style="color: var(--mut)">{{ parNiveau[cle] }}</span></div>
            <div class="trk"><div class="fl" :class="cle === 'faible' ? 'g' : cle === 'modéré' ? 'gd' : 'o'" :style="{ width: pourcent(parNiveau[cle]) + '%' }"></div></div>
          </div>
        </div>
      </div>
    </div>

    <div class="card">
      <div class="ch"><h3>Registre des risques</h3></div>
      <table>
        <thead><tr><th>N°</th><th>Danger</th><th>Catégorie</th><th>P</th><th>G</th><th>C</th><th>Niveau</th><th>Mesures</th></tr></thead>
        <tbody>
          <tr v-for="r in listeTriee" :key="r.id">
            <td>{{ r.numero }}</td>
            <td><b>{{ r.danger }}</b></td>
            <td>{{ r.categorie }}</td>
            <td>{{ r.derniere_cotation?.probabilite ?? "—" }}</td>
            <td>{{ r.derniere_cotation?.gravite ?? "—" }}</td>
            <td><b>{{ r.derniere_cotation?.criticite ?? "—" }}</b></td>
            <td><span class="tag" :class="TAG_NIVEAU[r.derniere_cotation?.niveau] ?? 't-gy'">{{ r.derniere_cotation?.niveau ?? "—" }}</span></td>
            <td class="sub">{{ r.derniere_cotation?.mesures_proposees?.slice(0, 60) ?? "—" }}</td>
          </tr>
          <tr v-if="!risques.chargement && !risques.liste.length"><td colspan="8" style="color: var(--mut)">Aucun risque enregistré.</td></tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

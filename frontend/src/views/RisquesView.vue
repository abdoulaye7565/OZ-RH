<script setup>
/**
 * Registre des risques — vue mobile (maquette #s-risques).
 *
 * Écart assumé : le "mtx" de la maquette est peuplé par script, sans markup
 * de référence — reconstruit ici directement à partir de GET /risques/matrice
 * (5×5, probabilité en ligne, gravité en colonne, comme l'indique la légende
 * "Probabilité ↑ · Gravité →").
 */
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import Icone from "../components/Icone.vue";
import Modal from "../components/Modal.vue";
import BandeauReseau from "../components/BandeauReseau.vue";
import { useRisquesStore } from "../stores/risques";

const router = useRouter();
const risques = useRisquesStore();
onMounted(() => risques.charger());

const CATEGORIES = [
  "Ergonomique", "Électrique", "Incendie", "Chute / Circulation", "Psychosocial (RPS)",
  "Manutention", "Ambiances physiques", "Hygiène / Biologique", "Sécurité de l'information",
  "Sécurité / Sûreté", "Routier / Trajet", "Incendie / Urgences",
];

const COULEUR_NIVEAU = { faible: "gr", modéré: "gd", élevé: "or", critique: "red" };
const TAG_NIVEAU = { faible: "t-gr", modéré: "t-gd", élevé: "t-or", critique: "t-red" };

function celluleMatrice(probabilite, gravite) {
  return risques.matrice.find((c) => c.probabilite === probabilite && c.gravite === gravite);
}

const nombreEleves = computed(
  () => risques.liste.filter((r) => ["élevé", "critique"].includes(r.derniere_cotation?.niveau)).length
);

const listeTriee = computed(() =>
  [...risques.liste].sort((a, b) => (b.derniere_cotation?.criticite ?? 0) - (a.derniere_cotation?.criticite ?? 0))
);

// --- Formulaire de création ---
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
      cotation: {
        probabilite: Number(nouveau.value.probabilite),
        gravite: Number(nouveau.value.gravite),
        mesures_proposees: nouveau.value.mesures_proposees,
      },
    });
    formulaireOuvert.value = false;
    nouveau.value = { danger: "", categorie: CATEGORIES[0], unite_travail: "", probabilite: 3, gravite: 3, mesures_proposees: "" };
  } catch (e) {
    erreurFormulaire.value = e instanceof Object && e.message ? e.message : "Impossible d'enregistrer ce risque";
  }
}
</script>

<template>
  <div class="ecran-mobile">
    <BandeauReseau />
    <header class="hd">
      <button class="back" aria-label="Retour" @click="router.push({ name: 'menu' })"><Icone nom="back" /></button>
      <div>
        <h1>Registre des risques</h1>
        <div class="sub">{{ risques.liste.length }} risques · cotation P × G</div>
      </div>
    </header>

    <div class="wrap">
      <div class="body">
        <div class="pad">
          <div v-if="risques.erreur" class="banner err">{{ risques.erreur }}</div>

          <div class="card" style="padding: 12px; margin-bottom: 12px">
            <div class="sec" style="margin-bottom: 8px">MATRICE DE CRITICITÉ</div>
            <div class="mtx">
              <template v-for="p in [5, 4, 3, 2, 1]" :key="p">
                <span class="ax">{{ p }}</span>
                <span
                  v-for="g in [1, 2, 3, 4, 5]"
                  :key="g"
                  class="tag"
                  :class="TAG_NIVEAU[celluleMatrice(p, g)?.niveau] ?? 't-gy'"
                  style="justify-content: center; padding: 6px 0"
                >
                  {{ celluleMatrice(p, g)?.risques?.length || "" }}
                </span>
              </template>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 9.5px; color: var(--mut); margin-top: 5px">
              <span>Probabilité ↑ · Gravité →</span><span>{{ nombreEleves }} risques élevés/critiques</span>
            </div>
          </div>

          <div v-for="r in listeTriee" :key="r.id" class="row">
            <span class="lead" :class="COULEUR_NIVEAU[r.derniere_cotation?.niveau] ?? 'gy'"><Icone nom="target" /></span>
            <div class="tx">
              <b>{{ r.danger }}</b>
              <div class="meta">
                <span v-if="r.derniere_cotation">P{{ r.derniere_cotation.probabilite }} × G{{ r.derniere_cotation.gravite }}</span>
                <span>{{ r.categorie }}</span>
                <span>{{ r.unite_travail }}</span>
              </div>
            </div>
            <span class="tag" :class="TAG_NIVEAU[r.derniere_cotation?.niveau] ?? 't-gy'">C {{ r.derniere_cotation?.criticite ?? "—" }}</span>
          </div>

          <div v-if="!risques.chargement && !risques.liste.length" class="empty">
            <div class="ic"><Icone nom="target" taille="lg" /></div>
            <b>Aucun risque enregistré</b>
          </div>

          <div style="height: 12px"></div>
          <button class="btn pri" @click="formulaireOuvert = true">
            <Icone nom="plus" taille="sm" />Ajouter ou réévaluer
          </button>

          <Modal v-if="formulaireOuvert" titre="Nouveau risque" @fermer="formulaireOuvert = false">
            <label class="f">Danger</label>
            <input v-model="nouveau.danger" class="inp" placeholder="Ex. Chute de hauteur" />
            <label class="f">Catégorie</label>
            <select v-model="nouveau.categorie" class="inp">
              <option v-for="c in CATEGORIES" :key="c" :value="c">{{ c }}</option>
            </select>
            <label class="f">Unité de travail</label>
            <input v-model="nouveau.unite_travail" class="inp" placeholder="Ex. Techniciens terrain" />
            <div style="display: flex; gap: 7px">
              <div style="flex: 1">
                <label class="f">Probabilité (1-5)</label>
                <select v-model="nouveau.probabilite" class="inp"><option v-for="n in [1, 2, 3, 4, 5]" :key="n" :value="n">{{ n }}</option></select>
              </div>
              <div style="flex: 1">
                <label class="f">Gravité (1-5)</label>
                <select v-model="nouveau.gravite" class="inp"><option v-for="n in [1, 2, 3, 4, 5]" :key="n" :value="n">{{ n }}</option></select>
              </div>
            </div>
            <label class="f">Mesures proposées</label>
            <textarea v-model="nouveau.mesures_proposees" class="inp" placeholder="Obligatoire"></textarea>
            <div v-if="erreurFormulaire" class="banner err" style="margin-top: 8px">{{ erreurFormulaire }}</div>
            <div class="btnrow" style="margin-top: 10px">
              <button class="btn pri sm" style="width: auto" @click="soumettre">Enregistrer</button>
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

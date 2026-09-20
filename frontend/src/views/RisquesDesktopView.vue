<script setup>
/**
 * Registre des risques — vue desktop (maquette #p-risk).
 *
 * Écart assumé : pas de colonne "Actions liées" (nécessiterait une jointure
 * non exposée par l'API actuelle) ; la formulaire d'ajout est repris de
 * RisquesView.vue plutôt que dupliqué avec un style desktop distinct.
 *
 * Recherche + pagination du registre ajoutées le 2026-09-09 (retour direct
 * de l'utilisateur — "les listes doivent avoir une possibilité de recherche,
 * les listes doivent être paginées") : écran pilote de
 * useRechercheEtPagination, avant extension aux autres écrans desktop à
 * liste (voir docs/JOURNAL.md).
 */
import { computed, onMounted, ref } from "vue";
import BarrePagination from "../components/BarrePagination.vue";
import Icone from "../components/Icone.vue";
import Modal from "../components/Modal.vue";
import { useRechercheEtPagination } from "../composables/useRechercheEtPagination";
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

// `numero` est un entier côté API : passer par String() avant toLowerCase(),
// sinon le prédicat lève et casse silencieusement la recherche (voir la mise
// en garde dans useRechercheEtPagination.js).
function correspond(r, terme) {
  return (
    r.danger?.toLowerCase().includes(terme) ||
    r.categorie?.toLowerCase().includes(terme) ||
    String(r.numero ?? "").toLowerCase().includes(terme) ||
    r.derniere_cotation?.mesures_proposees?.toLowerCase().includes(terme)
  );
}
const { recherche, page, totalPages, resultats, elementsPage, allerPage } =
  useRechercheEtPagination(listeTriee, correspond, 10);

const formulaireOuvert = ref(false);
const nouveau = ref({ danger: "", categorie: CATEGORIES[0], unite_travail: "", probabilite: 3, gravite: 3, mesures_proposees: "" });
const erreurFormulaire = ref(null);

// --- Correction des champs descriptifs (2026-09-10) : la cotation reste
// gérée par "réévaluer", jamais modifiée en place (historique, §5.2.5). ---
const edition = ref(null); // le risque en cours d'édition, ou null
const champsEdition = ref({ danger: "", categorie: "", unite_travail: "", personnes_exposees: "" });
const erreurEdition = ref(null);

function ouvrirEdition(r) {
  edition.value = r;
  champsEdition.value = {
    danger: r.danger,
    categorie: r.categorie,
    unite_travail: r.unite_travail,
    personnes_exposees: r.personnes_exposees ?? "",
  };
  erreurEdition.value = null;
}
async function soumettreEdition() {
  erreurEdition.value = null;
  try {
    await risques.modifier(edition.value.id, {
      danger: champsEdition.value.danger,
      categorie: champsEdition.value.categorie,
      unite_travail: champsEdition.value.unite_travail,
      personnes_exposees: champsEdition.value.personnes_exposees || null,
    });
    edition.value = null;
  } catch (e) {
    erreurEdition.value = e?.message ?? "Impossible d'enregistrer la correction";
  }
}

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
      <button class="btn pri" style="width: auto; margin-left: auto" @click="formulaireOuvert = true">
        <Icone nom="plus" taille="sm" />Ajouter un risque
      </button>
    </div>

    <div v-if="risques.erreur" class="banner err">{{ risques.erreur }}</div>

    <Modal v-if="formulaireOuvert" titre="Nouveau risque" @fermer="formulaireOuvert = false">
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
      <div style="display: flex; gap: 8px; margin-top: 10px">
        <button class="btn pri" style="width: auto" @click="soumettre">Enregistrer</button>
        <button class="btn gh" style="width: auto" @click="formulaireOuvert = false">Annuler</button>
      </div>
    </Modal>

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
      <div class="ch">
        <h3>Registre des risques</h3>
        <span style="flex: 1"></span>
        <div class="srch">
          <Icone nom="search" taille="sm" />
          <input v-model="recherche" placeholder="Rechercher un danger, une catégorie…" />
        </div>
      </div>
      <table>
        <thead><tr><th>N°</th><th>Danger</th><th>Catégorie</th><th>P</th><th>G</th><th>C</th><th>Niveau</th><th>Mesures</th><th></th></tr></thead>
        <tbody>
          <tr v-for="r in elementsPage" :key="r.id">
            <td>{{ r.numero }}</td>
            <td><b>{{ r.danger }}</b></td>
            <td>{{ r.categorie }}</td>
            <td>{{ r.derniere_cotation?.probabilite ?? "—" }}</td>
            <td>{{ r.derniere_cotation?.gravite ?? "—" }}</td>
            <td><b>{{ r.derniere_cotation?.criticite ?? "—" }}</b></td>
            <td><span class="tag" :class="TAG_NIVEAU[r.derniere_cotation?.niveau] ?? 't-gy'">{{ r.derniere_cotation?.niveau ?? "—" }}</span></td>
            <td class="sub">{{ r.derniere_cotation?.mesures_proposees?.slice(0, 60) ?? "—" }}</td>
            <td style="text-align: right"><button class="btn gh sm" style="width: auto" @click="ouvrirEdition(r)">Modifier</button></td>
          </tr>
          <tr v-if="!risques.chargement && !risques.liste.length"><td colspan="9" style="color: var(--mut)">Aucun risque enregistré.</td></tr>
          <tr v-if="risques.liste.length && !resultats.length"><td colspan="9" style="color: var(--mut)">Aucun risque ne correspond à la recherche.</td></tr>
        </tbody>
      </table>
      <BarrePagination :page="page" :total-pages="totalPages" @changer="allerPage">
        {{ resultats.length }} sur {{ risques.liste.length }} risque{{ risques.liste.length > 1 ? "s" : "" }} affiché{{ resultats.length > 1 ? "s" : "" }}
      </BarrePagination>
    </div>

    <Modal v-if="edition" :titre="`Corriger le risque ${edition.numero}`" @fermer="edition = null">
      <p class="sub" style="margin-bottom: 8px">
        Corrige la description. Pour changer la cotation (probabilité / gravité), utilise « réévaluer » —
        l'historique des cotations est conservé.
      </p>
      <label class="f">Danger</label>
      <input v-model="champsEdition.danger" class="inp" />
      <label class="f">Catégorie</label>
      <select v-model="champsEdition.categorie" class="inp"><option v-for="c in CATEGORIES" :key="c" :value="c">{{ c }}</option></select>
      <label class="f">Unité de travail</label>
      <input v-model="champsEdition.unite_travail" class="inp" />
      <label class="f">Personnes exposées (facultatif)</label>
      <input v-model="champsEdition.personnes_exposees" class="inp" />
      <div v-if="erreurEdition" class="banner err" style="margin: 8px 0">{{ erreurEdition }}</div>
      <div style="display: flex; gap: 8px; margin-top: 10px">
        <button class="btn pri" style="width: auto" @click="soumettreEdition">Enregistrer</button>
        <button class="btn gh" style="width: auto" @click="edition = null">Annuler</button>
      </div>
    </Modal>
  </div>
</template>

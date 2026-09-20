<script setup>
/**
 * Déchets & environnement — vue desktop (maquette #p-dechets).
 *
 * Écart assumé : la maquette n'a pas de formulaire de création visible
 * (données figées) — ajouté un formulaire repliable au-dessus du tableau,
 * même principe que ParcDesktopView.vue. "Incidents environnement" (4e
 * indicateur de la maquette) n'a pas d'entité dédiée côté backend : affiché
 * à 0 fixe avec une note, plutôt qu'inventé.
 */
import { computed, onMounted, ref } from "vue";
import BarrePagination from "../components/BarrePagination.vue";
import Icone from "../components/Icone.vue";
import Modal from "../components/Modal.vue";
import ModalConfirmation from "../components/ModalConfirmation.vue";
import { useRechercheEtPagination } from "../composables/useRechercheEtPagination";
import { useDechetsStore } from "../stores/dechets";
import { formaterDateCivile } from "../utils/dates";

const dechets = useDechetsStore();
onMounted(() => dechets.charger());

function correspond(d, terme) {
  return (
    d.type?.toLowerCase().includes(terme) ||
    d.description?.toLowerCase().includes(terme) ||
    d.filiere?.toLowerCase().includes(terme) ||
    (dechets.nomSite(d.site_id) ?? "").toLowerCase().includes(terme)
  );
}
const { recherche, page, totalPages, resultats, elementsPage, allerPage } =
  useRechercheEtPagination(computed(() => dechets.liste), correspond, 12);

const totalKg = computed(() => dechets.enStock.length);
const tauxJustificatifs = computed(() => {
  if (!dechets.enleves.length) return 100;
  return Math.round((dechets.enleves.filter((d) => d.justificatif).length / dechets.enleves.length) * 100);
});

const formulaireOuvert = ref(false);
const nouveau = ref({ date: new Date().toISOString().slice(0, 10), type: "", description: "", quantite: "", site_id: "", filiere: "" });
const erreurFormulaire = ref(null);

async function soumettre() {
  erreurFormulaire.value = null;
  try {
    await dechets.creer({ ...nouveau.value, site_id: Number(nouveau.value.site_id) });
    formulaireOuvert.value = false;
    nouveau.value = { date: new Date().toISOString().slice(0, 10), type: "", description: "", quantite: "", site_id: "", filiere: "" };
  } catch (e) {
    erreurFormulaire.value = e?.message ?? "Impossible d'enregistrer ce lot de déchets";
  }
}

const enlevementEnCours = ref(null);
const dateEnlevement = ref(new Date().toISOString().slice(0, 10));

// --- Correction / archivage d'un lot (2026-09-10) ---
const edition = ref(null);
const champsEdition = ref({ date: "", type: "", description: "", quantite: "", site_id: "", filiere: "" });
const erreurEdition = ref(null);

function ouvrirEdition(d) {
  edition.value = d;
  champsEdition.value = {
    date: d.date, type: d.type, description: d.description,
    quantite: d.quantite, site_id: d.site_id, filiere: d.filiere,
  };
  erreurEdition.value = null;
}
async function soumettreEdition() {
  erreurEdition.value = null;
  try {
    await dechets.modifier(edition.value.id, { ...champsEdition.value, site_id: Number(champsEdition.value.site_id) });
    edition.value = null;
  } catch (e) {
    erreurEdition.value = e?.message ?? "Impossible d'enregistrer la correction";
  }
}
const aArchiver = ref(null);
async function confirmerArchivage() {
  const d = aArchiver.value;
  aArchiver.value = null;
  try {
    await dechets.archiver(d.id);
  } catch (e) {
    dechets.erreur = e?.message ?? "Impossible d'archiver ce lot";
  }
}

async function confirmerEnlevement(item) {
  await dechets.enregistrerEnlevement(item.id, dateEnlevement.value, null);
  enlevementEnCours.value = null;
}
</script>

<template>
  <div>
    <div v-if="dechets.erreur" class="banner err">{{ dechets.erreur }}</div>

    <div class="mets" style="grid-template-columns: repeat(4, 1fr)">
      <div class="met">
        <div class="hd"><span class="ic m-gd"><Icone nom="inbox" taille="sm" /></span>Lots en stock</div>
        <div class="v">{{ totalKg }}</div>
        <div class="t down">enlèvement à planifier</div>
      </div>
      <div class="met">
        <div class="hd"><span class="ic m-gr"><Icone nom="recycle" taille="sm" /></span>Enlèvements</div>
        <div class="v">{{ dechets.enleves.length }}</div>
        <div class="t flat">filières agréées</div>
      </div>
      <div class="met">
        <div class="hd"><span class="ic m-gr"><Icone nom="doc" taille="sm" /></span>Justificatifs archivés</div>
        <div class="v">{{ tauxJustificatifs }} %</div>
        <div class="t up">traçabilité complète</div>
      </div>
      <div class="met">
        <div class="hd"><span class="ic m-bl"><Icone nom="shield" taille="sm" /></span>Incidents environnement</div>
        <div class="v">0</div>
        <div class="t up">aucun suivi dédié pour l'instant</div>
      </div>
    </div>

    <Modal v-if="formulaireOuvert" titre="Nouvel enregistrement" @fermer="formulaireOuvert = false">
      <div class="grid2">
        <div>
          <label class="f">Date</label><input v-model="nouveau.date" type="date" class="inp" />
          <label class="f">Type</label><input v-model="nouveau.type" class="inp" placeholder="DEEE, Batteries, Cartouches…" />
          <label class="f">Description</label><input v-model="nouveau.description" class="inp" />
        </div>
        <div>
          <label class="f">Quantité</label><input v-model="nouveau.quantite" class="inp" placeholder="14 kg, 4 unités…" />
          <label class="f">Site</label>
          <select v-model="nouveau.site_id" class="inp">
            <option value="" disabled>Choisir…</option>
            <option v-for="s in dechets.sites" :key="s.id" :value="s.id">{{ s.nom }}</option>
          </select>
          <label class="f">Filière / repreneur</label><input v-model="nouveau.filiere" class="inp" />
        </div>
      </div>
      <div v-if="erreurFormulaire" class="banner err" style="margin-top: 8px">{{ erreurFormulaire }}</div>
      <div style="display: flex; gap: 8px; margin-top: 10px">
        <button class="btn pri" style="width: auto" @click="soumettre">Enregistrer</button>
        <button class="btn gh" style="width: auto" @click="formulaireOuvert = false">Annuler</button>
      </div>
    </Modal>

    <div class="card">
      <div class="ch">
        <Icone nom="recycle" style="color: var(--green)" /><h3>Registre de gestion des déchets</h3>
        <span style="flex: 1"></span>
        <div class="srch">
          <Icone nom="search" taille="sm" />
          <input v-model="recherche" placeholder="Rechercher un type, une filière…" />
        </div>
        <span
          class="r"
          style="cursor: pointer"
          role="button"
          tabindex="0"
          @click="formulaireOuvert = true"
          @keydown.enter="formulaireOuvert = true"
        >Nouvel enregistrement</span>
      </div>
      <table>
        <thead>
          <tr><th>Date</th><th>Type</th><th>Description</th><th>Quantité</th><th>Site</th><th>Filière / repreneur</th><th>Enlèvement</th><th>Justificatif</th><th></th></tr>
        </thead>
        <tbody>
          <tr v-for="d in elementsPage" :key="d.id">
            <td>{{ formaterDateCivile(d.date) }}</td>
            <td><span class="tag t-gd">{{ d.type }}</span></td>
            <td>{{ d.description }}</td>
            <td>{{ d.quantite }}</td>
            <td>{{ dechets.nomSite(d.site_id) ?? `Site #${d.site_id}` }}</td>
            <td>{{ d.filiere || "—" }}</td>
            <td>
              <span v-if="d.date_enlevement" class="tag t-gr">{{ formaterDateCivile(d.date_enlevement) }}</span>
              <span v-else-if="enlevementEnCours === d.id" style="display: inline-flex; gap: 6px; align-items: center">
                <input v-model="dateEnlevement" type="date" class="inp" style="width: 130px; padding: 4px 6px" />
                <button class="btn pri sm" style="width: auto" @click="confirmerEnlevement(d)">OK</button>
              </span>
              <span
                v-else
                class="tag t-or"
                style="cursor: pointer"
                role="button"
                tabindex="0"
                @click="enlevementEnCours = d.id"
                @keydown.enter="enlevementEnCours = d.id"
              >À planifier</span>
            </td>
            <td><span class="tag" :class="d.justificatif ? 't-gr' : 't-gy'">{{ d.justificatif ? "Reçu" : "—" }}</span></td>
            <td style="text-align: right; white-space: nowrap">
              <button class="btn gh sm" style="width: auto" @click="ouvrirEdition(d)">Modifier</button>
              <button class="btn gh sm" style="width: auto; margin-left: 6px" @click="aArchiver = d">Archiver</button>
            </td>
          </tr>
          <tr v-if="!dechets.chargement && !dechets.liste.length"><td colspan="9" style="color: var(--mut)">Aucun déchet enregistré.</td></tr>
          <tr v-if="dechets.liste.length && !resultats.length"><td colspan="9" style="color: var(--mut)">Aucun déchet ne correspond à la recherche.</td></tr>
        </tbody>
      </table>
      <BarrePagination :page="page" :total-pages="totalPages" @changer="allerPage">
        {{ resultats.length }} sur {{ dechets.liste.length }} enregistrements · DEEE et batteries : filières agréées obligatoires
      </BarrePagination>
    </div>

    <Modal v-if="edition" titre="Corriger le lot de déchets" @fermer="edition = null">
      <div class="grid2">
        <div>
          <label class="f">Date</label><input v-model="champsEdition.date" type="date" class="inp" />
          <label class="f">Type</label><input v-model="champsEdition.type" class="inp" />
          <label class="f">Description</label><input v-model="champsEdition.description" class="inp" />
        </div>
        <div>
          <label class="f">Quantité</label><input v-model="champsEdition.quantite" class="inp" />
          <label class="f">Site</label>
          <select v-model="champsEdition.site_id" class="inp">
            <option v-for="s in dechets.sites" :key="s.id" :value="s.id">{{ s.nom }}</option>
          </select>
          <label class="f">Filière / repreneur</label><input v-model="champsEdition.filiere" class="inp" />
        </div>
      </div>
      <div v-if="erreurEdition" class="banner err" style="margin: 8px 0">{{ erreurEdition }}</div>
      <div style="display: flex; gap: 8px; margin-top: 10px">
        <button class="btn pri" style="width: auto" @click="soumettreEdition">Enregistrer</button>
        <button class="btn gh" style="width: auto" @click="edition = null">Annuler</button>
      </div>
    </Modal>

    <ModalConfirmation
      v-if="aArchiver"
      titre="Archiver le lot de déchets"
      :message="`Archiver ce lot (${aArchiver.type}) ? Il n'apparaîtra plus dans le registre courant.`"
      libelle-confirmer="Archiver"
      @confirmer="confirmerArchivage"
      @annuler="aArchiver = null"
    />
  </div>
</template>

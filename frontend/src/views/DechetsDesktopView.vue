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
import Icone from "../components/Icone.vue";
import { useDechetsStore } from "../stores/dechets";
import { formaterDateCivile } from "../utils/dates";

const dechets = useDechetsStore();
onMounted(() => dechets.charger());

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

    <div v-if="formulaireOuvert" class="card">
      <div class="ch"><h3>Nouvel enregistrement</h3></div>
      <div class="cb">
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
        <button class="btn pri" style="width: auto; margin-top: 10px" @click="soumettre">Enregistrer</button>
      </div>
    </div>

    <div class="card">
      <div class="ch">
        <Icone nom="recycle" style="color: var(--green)" /><h3>Registre de gestion des déchets</h3>
        <span
          class="r"
          style="cursor: pointer"
          role="button"
          tabindex="0"
          @click="formulaireOuvert = !formulaireOuvert"
          @keydown.enter="formulaireOuvert = !formulaireOuvert"
        >Nouvel enregistrement</span>
      </div>
      <table>
        <thead>
          <tr><th>Date</th><th>Type</th><th>Description</th><th>Quantité</th><th>Site</th><th>Filière / repreneur</th><th>Enlèvement</th><th>Justificatif</th></tr>
        </thead>
        <tbody>
          <tr v-for="d in dechets.liste" :key="d.id">
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
          </tr>
          <tr v-if="!dechets.chargement && !dechets.liste.length"><td colspan="8" style="color: var(--mut)">Aucun déchet enregistré.</td></tr>
        </tbody>
      </table>
      <div class="pagin"><span>{{ dechets.liste.length }} enregistrements · DEEE et batteries : filières agréées obligatoires</span></div>
    </div>
  </div>
</template>

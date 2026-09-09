<script setup>
/**
 * Parc & configurations — vue desktop (maquette #p-parc).
 *
 * Écart assumé : la fiche équipement (clic sur une ligne) réutilise l'écran
 * mobile ParcFicheView.vue plutôt qu'un écran desktop dédié — construire les
 * deux fiches en parallèle aurait retardé les modules encore non commencés ;
 * la fiche mobile reste pleinement fonctionnelle, seulement pas habillée au
 * style desktop.
 */
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import Icone from "../components/Icone.vue";
import { useParcStore } from "../stores/parc";
import { formaterDateCivile } from "../utils/dates";

const router = useRouter();
const parc = useParcStore();
onMounted(() => parc.charger());

const MARQUES = ["MikroTik", "Grandstream", "Ubiquiti", "Ruijie", "autre"];
const filtreMarque = ref("Tous");
const listeFiltree = computed(() => (filtreMarque.value === "Tous" ? parc.liste : parc.liste.filter((e) => e.marque === filtreMarque.value)));

const formulaireOuvert = ref(false);
const nouveau = ref({ identity: "", marque: "MikroTik", modele: "", numero_serie: "", site_id: "", emplacement: "", date_installation: "" });
const erreurFormulaire = ref(null);

async function soumettre() {
  erreurFormulaire.value = null;
  try {
    await parc.creerEquipement({ ...nouveau.value, site_id: Number(nouveau.value.site_id) });
    formulaireOuvert.value = false;
    nouveau.value = { identity: "", marque: "MikroTik", modele: "", numero_serie: "", site_id: "", emplacement: "", date_installation: "" };
  } catch (e) {
    erreurFormulaire.value = e?.message ?? "Impossible d'enregistrer cet équipement";
  }
}
</script>

<template>
  <div>
    <div v-if="parc.erreur" class="banner err">{{ parc.erreur }}</div>

    <div class="filters">
      <button class="seg" :class="{ on: filtreMarque === 'Tous' }" @click="filtreMarque = 'Tous'">Tous · {{ parc.liste.length }}</button>
      <button v-for="m in MARQUES" :key="m" class="seg" :class="{ on: filtreMarque === m }" @click="filtreMarque = m">{{ m }}</button>
      <span style="flex: 1"></span>
      <button class="btn pri sm" style="width: auto" @click="formulaireOuvert = !formulaireOuvert"><Icone nom="plus" taille="sm" />Nouvel équipement</button>
    </div>

    <div v-if="formulaireOuvert" class="card">
      <div class="ch"><h3>Nouvel équipement</h3></div>
      <div class="cb">
        <div class="grid2">
          <div>
            <label class="f">Identity (SITE-FONCTION-NN)</label>
            <input v-model="nouveau.identity" class="inp" placeholder="Ex. KAT-ST-01" />
            <label class="f">Marque</label>
            <select v-model="nouveau.marque" class="inp"><option v-for="m in MARQUES" :key="m" :value="m">{{ m }}</option></select>
            <label class="f">Modèle</label>
            <input v-model="nouveau.modele" class="inp" />
            <label class="f">Numéro de série</label>
            <input v-model="nouveau.numero_serie" class="inp" />
          </div>
          <div>
            <label class="f">Site</label>
            <select v-model="nouveau.site_id" class="inp">
              <option value="" disabled>Choisir…</option>
              <option v-for="s in parc.sites" :key="s.id" :value="s.id">{{ s.nom }}</option>
            </select>
            <label class="f">Emplacement</label>
            <input v-model="nouveau.emplacement" class="inp" />
            <label class="f">Date d'installation</label>
            <input v-model="nouveau.date_installation" type="date" class="inp" />
          </div>
        </div>
        <div v-if="erreurFormulaire" class="banner err" style="margin-top: 8px">{{ erreurFormulaire }}</div>
        <button class="btn pri" style="width: auto; margin-top: 10px" @click="soumettre">Enregistrer</button>
      </div>
    </div>

    <div class="card">
      <table>
        <thead><tr><th>Identity</th><th>Marque / modèle</th><th>Site</th><th>Emplacement</th><th>Installé le</th><th>Statut</th></tr></thead>
        <tbody>
          <tr v-for="e in listeFiltree" :key="e.id" style="cursor: pointer" @click="router.push({ name: 'parc-fiche', params: { id: e.id } })">
            <td><b>{{ e.identity }}</b></td>
            <td>{{ e.marque }} {{ e.modele }}</td>
            <td>{{ parc.nomSite(e.site_id) ?? `Site #${e.site_id}` }}</td>
            <td>{{ e.emplacement }}</td>
            <td>{{ formaterDateCivile(e.date_installation) }}</td>
            <td><span class="tag" :class="e.statut === 'en_service' ? 't-gr' : 't-or'">{{ e.statut }}</span></td>
          </tr>
          <tr v-if="!parc.chargement && !listeFiltree.length"><td colspan="6" style="color: var(--mut)">Aucun équipement.</td></tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

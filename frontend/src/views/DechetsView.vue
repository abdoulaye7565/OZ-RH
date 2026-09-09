<script setup>
/**
 * Déchets & environnement — vue mobile (maquette #s-dechets).
 *
 * Écart assumé : la maquette montre 3 lignes fixes (bac DEEE en stock, deux
 * enlèvements tracés) sans formulaire de saisie visible dans le fragment —
 * ajouté ici un formulaire d'enregistrement (mêmes champs que la table
 * desktop #p-dechets : date, type, description, quantité, site, filière)
 * plus l'action "Enlèvement" sur les lots encore en stock, cohérent avec
 * les routes réelles (POST /dechets, POST /dechets/{id}/enlevement).
 */
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import Icone from "../components/Icone.vue";
import BandeauReseau from "../components/BandeauReseau.vue";
import { useDechetsStore } from "../stores/dechets";
import { formaterDateCivile } from "../utils/dates";

const router = useRouter();
const dechets = useDechetsStore();
onMounted(() => dechets.charger());

const formaterDate = formaterDateCivile;

const totalEnStock = computed(() => dechets.enStock.length);
const totalEnleves = computed(() => dechets.enleves.length);
const tauxJustificatifs = computed(() => {
  if (!dechets.enleves.length) return 100;
  return Math.round((dechets.enleves.filter((d) => d.justificatif).length / dechets.enleves.length) * 100);
});

// --- Formulaire de création ---
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
  <div class="ecran-mobile">
    <BandeauReseau />
    <header class="hd">
      <button class="back" aria-label="Retour" @click="router.push({ name: 'menu' })"><Icone nom="back" /></button>
      <div>
        <h1>Déchets &amp; environnement</h1>
        <div class="sub">Registre DEEE</div>
      </div>
    </header>

    <div class="wrap">
      <div class="body">
        <div class="pad">
          <div v-if="dechets.erreur" class="banner err">{{ dechets.erreur }}</div>
          <div v-else-if="dechets.chargement" class="skel" style="height: 64px"></div>

          <div class="metrics">
            <div class="met"><div class="v">{{ totalEnStock }}</div><div class="l">lots en stock</div></div>
            <div class="met"><div class="v">{{ totalEnleves }}</div><div class="l">enlèvements</div></div>
            <div class="met g"><div class="v">{{ tauxJustificatifs }}%</div><div class="l">justificatifs</div></div>
          </div>
          <div style="height: 14px"></div>

          <div v-for="d in dechets.liste" :key="d.id">
            <div
              class="row"
              :role="!d.date_enlevement ? 'button' : undefined"
              :tabindex="!d.date_enlevement ? 0 : undefined"
              @click="!d.date_enlevement && (enlevementEnCours = enlevementEnCours === d.id ? null : d.id)"
              @keydown.enter="!d.date_enlevement && (enlevementEnCours = enlevementEnCours === d.id ? null : d.id)"
            >
              <span class="lead" :class="d.date_enlevement ? 'gr' : 'gd'"><Icone :nom="d.date_enlevement ? 'recycle' : 'inbox'" /></span>
              <div class="tx">
                <b>{{ d.type }} — {{ d.description }}</b>
                <div class="meta">
                  <span>{{ d.quantite }}</span>
                  <span>{{ dechets.nomSite(d.site_id) ?? `Site #${d.site_id}` }}</span>
                  <span v-if="d.date_enlevement">Enlevé le {{ formaterDate(d.date_enlevement) }}</span>
                </div>
              </div>
              <span class="tag" :class="d.date_enlevement ? 't-gr' : 't-gd'">{{ d.date_enlevement ? "TRACÉ" : "EN STOCK" }}</span>
            </div>
            <div v-if="enlevementEnCours === d.id" class="card" style="padding: 11px; margin: -4px 0 10px">
              <label class="f">Date d'enlèvement</label>
              <input v-model="dateEnlevement" type="date" class="inp" />
              <div class="btnrow" style="margin-top: 8px">
                <button class="btn pri sm" style="width: auto" @click.stop="confirmerEnlevement(d)">Confirmer</button>
                <button class="btn gh sm" style="width: auto" @click.stop="enlevementEnCours = null">Annuler</button>
              </div>
            </div>
          </div>

          <div v-if="!dechets.chargement && !dechets.liste.length" class="empty">
            <div class="ic"><Icone nom="recycle" taille="lg" /></div>
            <b>Aucun déchet enregistré</b>
          </div>

          <div v-if="!formulaireOuvert" style="height: 12px"></div>
          <button v-if="!formulaireOuvert" class="btn pri" @click="formulaireOuvert = true">
            <Icone nom="plus" taille="sm" />Enregistrer un déchet
          </button>

          <div v-if="formulaireOuvert" class="card" style="padding: 13px; margin-top: 4px">
            <label class="f">Date</label><input v-model="nouveau.date" type="date" class="inp" />
            <label class="f">Type</label><input v-model="nouveau.type" class="inp" placeholder="DEEE, Batteries, Cartouches…" />
            <label class="f">Description</label><input v-model="nouveau.description" class="inp" />
            <label class="f">Quantité</label><input v-model="nouveau.quantite" class="inp" placeholder="14 kg, 4 unités…" />
            <label class="f">Site</label>
            <select v-model="nouveau.site_id" class="inp">
              <option value="" disabled>Sélectionner…</option>
              <option v-for="s in dechets.sites" :key="s.id" :value="s.id">{{ s.nom }}</option>
            </select>
            <label class="f">Filière / repreneur</label><input v-model="nouveau.filiere" class="inp" />
            <div v-if="erreurFormulaire" class="banner err" style="margin: 8px 0">{{ erreurFormulaire }}</div>
            <div class="btnrow" style="margin-top: 8px">
              <button class="btn pri sm" style="width: auto" @click="soumettre">Enregistrer</button>
              <button class="btn gh sm" style="width: auto" @click="formulaireOuvert = false">Annuler</button>
            </div>
          </div>

          <div class="banner info" style="margin-top: 11px">
            <Icone nom="recycle" taille="sm" style="margin-top: 1px" />
            <div>DEEE et batteries : filières agréées uniquement, jamais aux ordures.</div>
          </div>

          <div style="height: 56px"></div>
        </div>
      </div>
    </div>

    <nav class="tabs">
      <button class="tb" @click="router.push({ name: 'accueil' })"><Icone nom="home" />Accueil</button>
      <button class="tb" @click="router.push({ name: 'signalements' })"><Icone nom="alert" />Signaux</button>
      <button class="tb" @click="router.push({ name: 'slam' })"><Icone nom="climb" />SLAM</button>
      <button class="tb" @click="router.push({ name: 'tableau-de-bord' })"><Icone nom="chart" />Tableau</button>
      <button class="tb" @click="router.push({ name: 'assistant-documentaire' })"><Icone nom="chat" />Assistant</button>
      <button class="tb" @click="router.push({ name: 'menu' })"><Icone nom="grid" />Menu</button>
    </nav>
  </div>
</template>

<script setup>
/**
 * Parc & configurations — vue mobile (maquette #s-parc).
 */
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import Icone from "../components/Icone.vue";
import BandeauReseau from "../components/BandeauReseau.vue";
import { useAuthStore } from "../stores/auth";
import { useParcStore } from "../stores/parc";

const router = useRouter();
const auth = useAuthStore();
const parc = useParcStore();
onMounted(() => parc.charger());

// Section 5.2.4 du CDC : le référent SHEQ n'a jamais accès au coffre-fort.
const peutVoirCoffreFort = computed(() => ["technicien", "responsable", "administrateur"].includes(auth.utilisateur?.role));

const MARQUES = ["MikroTik", "Grandstream", "Ubiquiti", "Ruijie", "autre"];
const filtreMarque = ref("Tous");
const recherche = ref("");

const listeFiltree = computed(() =>
  parc.liste.filter((e) => {
    if (filtreMarque.value !== "Tous" && e.marque !== filtreMarque.value) return false;
    if (!recherche.value.trim()) return true;
    const q = recherche.value.toLowerCase();
    return e.identity.toLowerCase().includes(q) || e.numero_serie.toLowerCase().includes(q) || (parc.nomSite(e.site_id) ?? "").toLowerCase().includes(q);
  })
);

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
  <div class="ecran-mobile">
    <BandeauReseau />
    <header class="hd">
      <div class="mk">H</div>
      <div>
        <h1>Parc &amp; configurations</h1>
        <div class="sub">{{ parc.liste.length }} équipements</div>
      </div>
    </header>

    <div class="wrap">
      <div class="body">
        <div class="pad">
          <div v-if="parc.erreur" class="banner err">{{ parc.erreur }}</div>

          <input v-model="recherche" class="inp" style="margin-bottom: 11px" placeholder="Identity, site, n° de série…" />
          <div class="segs" style="margin-bottom: 12px">
            <button class="seg" :class="{ on: filtreMarque === 'Tous' }" @click="filtreMarque = 'Tous'">Tous</button>
            <button v-for="m in MARQUES" :key="m" class="seg" :class="{ on: filtreMarque === m }" @click="filtreMarque = m">{{ m }}</button>
          </div>

          <div v-for="e in listeFiltree" :key="e.id" class="row" role="button" tabindex="0" @click="router.push({ name: 'parc-fiche', params: { id: e.id } })" @keydown.enter="router.push({ name: 'parc-fiche', params: { id: e.id } })">
            <span class="lead nv"><Icone nom="antenna" /></span>
            <div class="tx">
              <b>{{ e.identity }} · {{ e.marque }} {{ e.modele }}</b>
              <div class="meta">
                <span>{{ parc.nomSite(e.site_id) ?? `Site #${e.site_id}` }}</span>
                <span>{{ e.emplacement }}</span>
                <span v-if="e.statut !== 'en_service'" style="color: var(--orange); font-weight: 650">{{ e.statut }}</span>
              </div>
            </div>
            <Icone nom="chev" />
          </div>

          <div v-if="!parc.chargement && !listeFiltree.length" class="empty">
            <div class="ic"><Icone nom="antenna" taille="lg" /></div>
            <b>Aucun équipement</b>
          </div>

          <div class="banner info" style="margin-top: 4px">
            <Icone nom="lock" taille="sm" style="margin-top: 1px" />
            <div>Les identifiants ne figurent jamais sur les fiches : ils sont conservés dans le coffre-fort chiffré.</div>
            <span v-if="peutVoirCoffreFort" class="act" @click="router.push({ name: 'coffre-fort' })">Ouvrir</span>
          </div>

          <div v-if="!formulaireOuvert" style="height: 12px"></div>
          <button v-if="!formulaireOuvert" class="btn pri" @click="formulaireOuvert = true"><Icone nom="plus" taille="sm" />Nouvel équipement</button>

          <div v-if="formulaireOuvert" class="card" style="padding: 13px; margin-top: 4px">
            <div class="sec" style="margin-bottom: 8px">NOUVEL ÉQUIPEMENT</div>
            <label class="f">Identity (SITE-FONCTION-NN)</label>
            <input v-model="nouveau.identity" class="inp" placeholder="Ex. KAT-ST-01" />
            <label class="f">Marque</label>
            <select v-model="nouveau.marque" class="inp"><option v-for="m in MARQUES" :key="m" :value="m">{{ m }}</option></select>
            <label class="f">Modèle</label>
            <input v-model="nouveau.modele" class="inp" />
            <label class="f">Numéro de série</label>
            <input v-model="nouveau.numero_serie" class="inp" />
            <label class="f">Site</label>
            <select v-model="nouveau.site_id" class="inp">
              <option value="" disabled>Choisir…</option>
              <option v-for="s in parc.sites" :key="s.id" :value="s.id">{{ s.nom }}</option>
            </select>
            <label class="f">Emplacement</label>
            <input v-model="nouveau.emplacement" class="inp" placeholder="Ex. Pylône, baie A…" />
            <label class="f">Date d'installation</label>
            <input v-model="nouveau.date_installation" type="date" class="inp" />
            <div v-if="erreurFormulaire" class="banner err" style="margin-top: 8px">{{ erreurFormulaire }}</div>
            <div class="btnrow" style="margin-top: 10px">
              <button class="btn pri sm" style="width: auto" @click="soumettre">Enregistrer</button>
              <button class="btn gh sm" style="width: auto" @click="formulaireOuvert = false">Annuler</button>
            </div>
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
      <button class="tb" @click="router.push({ name: 'menu' })"><Icone nom="grid" />Menu</button>
    </nav>
  </div>
</template>

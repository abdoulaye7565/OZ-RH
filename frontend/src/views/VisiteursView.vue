<script setup>
/**
 * Visiteurs — vue mobile (maquette #s-visit).
 */
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import Icone from "../components/Icone.vue";
import BandeauReseau from "../components/BandeauReseau.vue";
import { useVisiteursStore } from "../stores/visiteurs";

const router = useRouter();
const visiteurs = useVisiteursStore();
onMounted(() => visiteurs.charger());

const nouveau = ref({ nom: "", societe: "", motif: "", personne_visitee: "", consignes_lues: false });
const erreur = ref(null);

async function soumettre() {
  erreur.value = null;
  try {
    await visiteurs.enregistrer(nouveau.value);
    nouveau.value = { nom: "", societe: "", motif: "", personne_visitee: "", consignes_lues: false };
  } catch (e) {
    erreur.value = e?.message ?? "Impossible d'enregistrer ce visiteur — les consignes de sécurité doivent être cochées";
  }
}

function formaterHeure(iso) {
  return new Date(iso).toLocaleTimeString("fr-FR", { hour: "2-digit", minute: "2-digit" });
}
</script>

<template>
  <div class="ecran-mobile">
    <BandeauReseau />
    <header class="hd">
      <button class="back" aria-label="Retour" @click="router.push({ name: 'menu' })"><Icone nom="back" /></button>
      <div>
        <h1>Visiteurs</h1>
        <div class="sub">{{ visiteurs.presents.length }} personne{{ visiteurs.presents.length > 1 ? "s" : "" }} sur site</div>
      </div>
    </header>

    <div class="wrap">
      <div class="body">
        <div class="pad">
          <div v-if="visiteurs.erreur" class="banner err">{{ visiteurs.erreur }}</div>

          <label class="f">Nom et prénom</label>
          <input v-model="nouveau.nom" class="inp" placeholder="Nom complet du visiteur" />
          <label class="f">Société / motif</label>
          <input v-model="nouveau.motif" class="inp" placeholder="Livraison, réunion…" />
          <label class="f">Société (facultatif)</label>
          <input v-model="nouveau.societe" class="inp" />
          <label class="f">Personne visitée</label>
          <input v-model="nouveau.personne_visitee" class="inp" />

          <div class="banner warn" style="margin-top: 13px">
            <Icone nom="shield" taille="sm" style="margin-top: 1px" />
            <div>
              <b>Consignes de sécurité</b><br />Issues de secours · point de rassemblement · zones interdites
              <label style="display: block; margin-top: 8px; font-weight: 650">
                <input v-model="nouveau.consignes_lues" type="checkbox" /> J'ai lu et j'accepte les consignes
              </label>
            </div>
          </div>

          <div v-if="erreur" class="banner err" style="margin-top: 8px">{{ erreur }}</div>
          <button class="btn gold" style="margin-top: 10px" @click="soumettre">J'accepte et je m'enregistre</button>

          <div class="sec" style="margin-top: 16px">SUR SITE <span class="n">{{ visiteurs.presents.length }}</span></div>
          <div v-for="v in visiteurs.presents" :key="v.id" class="row" role="button" tabindex="0" @click="visiteurs.enregistrerDepart(v.id)" @keydown.enter="visiteurs.enregistrerDepart(v.id)">
            <span class="lead nv"><Icone nom="door" /></span>
            <div class="tx">
              <b>{{ v.nom }}{{ v.societe ? ` — ${v.societe}` : "" }}</b>
              <div class="meta"><span>Arrivé {{ formaterHeure(v.heure_arrivee) }}</span><span>{{ v.motif }}</span></div>
            </div>
            <span class="tag t-gr">PRÉSENT</span>
          </div>
          <p v-if="!visiteurs.presents.length" style="font-size: 12px; color: var(--mut)">Aucun visiteur sur site — cliquer une ligne enregistre le départ.</p>

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

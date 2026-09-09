<script setup>
/**
 * Visiteurs — vue desktop (maquette #p-visit).
 */
import { onMounted, ref } from "vue";
import Icone from "../components/Icone.vue";
import { useVisiteursStore } from "../stores/visiteurs";

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
    erreur.value = e?.message ?? "Impossible d'enregistrer ce visiteur — les consignes doivent être cochées";
  }
}
function formaterHeure(iso) {
  return new Date(iso).toLocaleTimeString("fr-FR", { hour: "2-digit", minute: "2-digit" });
}
</script>

<template>
  <div>
    <div v-if="visiteurs.erreur" class="banner err">{{ visiteurs.erreur }}</div>
    <div class="grid2">
      <div class="card">
        <div class="ch"><Icone nom="door" /><h3>Nouveau visiteur</h3></div>
        <div class="cb">
          <label class="f">Nom et prénom</label><input v-model="nouveau.nom" class="inp" />
          <label class="f">Motif</label><input v-model="nouveau.motif" class="inp" />
          <label class="f">Société</label><input v-model="nouveau.societe" class="inp" />
          <label class="f">Personne visitée</label><input v-model="nouveau.personne_visitee" class="inp" />
          <label style="display: block; margin: 10px 0; font-size: 12.5px; font-weight: 650">
            <input v-model="nouveau.consignes_lues" type="checkbox" /> Consignes de sécurité lues et acceptées
          </label>
          <div v-if="erreur" class="banner err" style="margin-bottom: 8px">{{ erreur }}</div>
          <button class="btn gold" style="width: auto" @click="soumettre">Enregistrer l'arrivée</button>
        </div>
      </div>
      <div class="card">
        <div class="ch"><Icone nom="shield" /><h3>Présents sur site</h3></div>
        <div class="cb">
          <div v-for="v in visiteurs.presents" :key="v.id" class="kv">
            <span>{{ v.nom }}{{ v.societe ? ` — ${v.societe}` : "" }} · {{ formaterHeure(v.heure_arrivee) }}</span>
            <button class="btn gh sm" style="width: auto" @click="visiteurs.enregistrerDepart(v.id)">Départ</button>
          </div>
          <p v-if="!visiteurs.presents.length" style="color: var(--mut); font-size: 12.5px">Aucun visiteur sur site.</p>
        </div>
      </div>
    </div>
  </div>
</template>

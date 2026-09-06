<script setup>
/**
 * Écran de validation d'un permis — maquette #s-permis, "vue responsable"
 * (figure A.6 du CDC). Les 4 lignes de contrôle viennent de
 * `controles.details` (backend, enrichi au prompt 2.3 pour cet écran
 * précisément — voir docs/JOURNAL.md) : chaque condition de la règle centrale
 * (prompt 2.2) est montrée avec son résultat, pas seulement celles en échec.
 *
 * Écart assumé : la maquette affiche les noms des intervenants ("A. Koné,
 * M. Sissoko") ; l'API ne renvoie que des identifiants (intervenant_ids),
 * affichés ici "Utilisateur #id" — même limite déjà signalée pour l'auteur
 * d'un signalement au prompt 1.3.
 */
import { computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import Icone from "../components/Icone.vue";
import BandeauReseau from "../components/BandeauReseau.vue";
import api from "../services/api";

const route = useRoute();
const router = useRouter();

const permis = ref(null);
const chargement = ref(true);
const erreur = ref(null);
const actionEnCours = ref(false);

async function charger() {
  chargement.value = true;
  erreur.value = null;
  try {
    permis.value = await api.requete(`/api/v1/permis/${route.params.id}`);
  } catch (e) {
    erreur.value = e instanceof api.ErreurApi ? e.message : "Impossible de charger le permis";
  } finally {
    chargement.value = false;
  }
}
onMounted(charger);

const details = computed(() => permis.value?.controles?.details ?? []);
const nombreConformes = computed(() => details.value.filter((d) => d.conforme).length);
const peutValider = computed(() => permis.value?.controles?.conforme === true);

function formaterHeure(iso) {
  return new Date(iso).toLocaleTimeString("fr-FR", { hour: "2-digit", minute: "2-digit" });
}

async function valider() {
  actionEnCours.value = true;
  erreur.value = null;
  try {
    permis.value = await api.requete(`/api/v1/permis/${permis.value.id}/valider`, { methode: "POST" });
  } catch (e) {
    if (e instanceof api.ErreurApi && e.statut === 409) {
      // Le serveur réévalue et peut renvoyer un blocage à jour : on recharge
      // pour refléter l'état réel plutôt que d'afficher un message figé.
      await charger();
    } else {
      erreur.value = e instanceof api.ErreurApi ? e.message : "Action impossible";
    }
  } finally {
    actionEnCours.value = false;
  }
}

</script>

<template>
  <div class="ecran-mobile">
    <BandeauReseau />
    <header class="hd">
      <button class="back" aria-label="Retour" @click="router.back()"><Icone nom="back" /></button>
      <div>
        <h1>Permis {{ permis?.reference ?? "…" }}</h1>
        <div class="sub" v-if="permis">Demande reçue à {{ formaterHeure(permis.cree_le) }}</div>
      </div>
    </header>

    <div class="body">
      <div class="pad">
        <div v-if="chargement">Chargement…</div>

        <template v-else-if="permis">
          <div class="card" style="padding: 12px; margin-bottom: 12px">
            <div class="kv"><span>Site</span><b>#{{ permis.site_id }}</b></div>
            <div class="kv"><span>Travaux</span><b>{{ permis.nature_travaux }}</b></div>
            <div class="kv">
              <span>Intervenants</span>
              <b>{{ permis.intervenant_ids.map((id) => `Utilisateur #${id}`).join(", ") }}</b>
            </div>
            <div class="kv">
              <span>Créneau</span>
              <b>{{ formaterHeure(permis.debut_validite) }} → {{ formaterHeure(permis.fin_validite) }}</b>
            </div>
          </div>

          <div class="sec">
            CONTRÔLES AUTOMATIQUES <span class="n">{{ nombreConformes }}/{{ details.length }}</span>
          </div>
          <ul class="cl">
            <li v-for="d in details" :key="d.cle" :class="d.conforme ? 'ok' : 'ko'">
              <span class="cb"><Icone :nom="d.conforme ? 'check' : 'x'" taille="sm" /></span>
              <span class="tx">{{ d.libelle }}<span v-if="d.detail"> — {{ d.detail }}</span></span>
            </li>
          </ul>

          <div v-if="!peutValider && permis.statut !== 'delivre'" class="banner err">
            <Icone nom="lock" taille="sm" style="margin-top: 1px" />
            <div><b>Validation bloquée.</b> Corrigez les points en rouge ci-dessus avant de réessayer.</div>
          </div>

          <div v-if="erreur" class="banner err">{{ erreur }}</div>

          <template v-if="permis.statut === 'delivre'">
            <div class="banner info">Ce permis a déjà été délivré.</div>
          </template>
          <template v-else>
            <button class="btn pri" :disabled="!peutValider || actionEnCours" @click="valider">
              <Icone nom="lock" v-if="!peutValider" taille="sm" />
              Valider et délivrer
            </button>
          </template>
        </template>
      </div>
    </div>
  </div>
</template>

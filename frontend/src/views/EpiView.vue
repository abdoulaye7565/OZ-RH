<script setup>
/**
 * EPI antichute — vue mobile (maquette #s-epi).
 *
 * Écart assumé : la maquette montre un unique bouton "Enregistrer une
 * vérification" en pied d'écran, sans préciser l'écran suivant (hors du
 * fragment fourni). Traduit ici par une action directe sur chaque ligne
 * (Conforme / Non conforme), plus rapide sur le terrain qu'un sélecteur
 * séparé — cohérent avec le principe general "deux minutes suffisent" déjà
 * appliqué à NouveauSignalementView.
 */
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import Icone from "../components/Icone.vue";
import BandeauReseau from "../components/BandeauReseau.vue";
import { useAuthStore } from "../stores/auth";
import { useEpiStore } from "../stores/epi";
import { formaterDateCivile, joursRestantsCivil } from "../utils/dates";

const router = useRouter();
const auth = useAuthStore();
const epi = useEpiStore();
const epiEnAction = ref(null);

onMounted(() => epi.charger());

const peutVerifier = computed(() => ["referent_sheq", "administrateur"].includes(auth.utilisateur?.role));

const ICONES_TYPE = {
  harnais: "vest",
  longe: "vest",
  antichute_mobile: "vest",
  casque: "shield",
  connecteur: "shield",
  ligne_de_vie: "vest",
};

const LIBELLES_TYPE = {
  harnais: "Harnais complet",
  longe: "Longe",
  antichute_mobile: "Antichute mobile",
  casque: "Casque",
  connecteur: "Connecteur",
  ligne_de_vie: "Ligne de vie",
};

const joursRestants = joursRestantsCivil;

function etat(item) {
  if (item.statut === "reforme") return { lead: "gy", tag: "t-gy", libelle: "RÉFORMÉ", icone: "x" };
  if (item.statut === "retire") return { lead: "gy", tag: "t-gy", libelle: "RETIRÉ", icone: "x" };
  const jours = joursRestants(item.prochaine_verification);
  if (jours !== null && jours < 0) return { lead: "red", tag: "t-red", libelle: "À VÉRIFIER", icone: "vest" };
  if (jours !== null && jours <= 7) return { lead: "or", tag: "t-or", libelle: `J−${jours}`, icone: "clock" };
  return { lead: "gr", tag: "t-gr", libelle: "EN SERVICE", icone: ICONES_TYPE[item.type] ?? "vest" };
}

const nombreAAgir = computed(
  () => epi.liste.filter((e) => e.statut !== "reforme" && e.statut !== "retire" && (joursRestants(e.prochaine_verification) ?? 99) <= 7).length
);

const formaterDate = formaterDateCivile;

function basculerAction(item) {
  epiEnAction.value = epiEnAction.value === item.id ? null : item.id;
}

async function verifier(item, conforme) {
  await epi.enregistrerVerification(item.id, conforme);
  epiEnAction.value = null;
}
</script>

<template>
  <div class="ecran-mobile">
    <BandeauReseau />
    <header class="hd">
      <button class="back" aria-label="Retour" @click="router.back()"><Icone nom="back" /></button>
      <div>
        <h1>EPI antichute</h1>
        <div class="sub">{{ epi.liste.length }} équipements suivis</div>
      </div>
    </header>

    <div class="wrap">
      <div class="body">
        <div class="pad">
          <div v-if="epi.erreur" class="banner err">{{ epi.erreur }}</div>
          <div v-else-if="epi.chargement" class="skel" style="height: 64px"></div>

          <div v-if="nombreAAgir > 0" class="banner warn">
            <Icone nom="alert" taille="sm" style="margin-top: 1px" />
            <div><b>{{ nombreAAgir }} EPI demande{{ nombreAAgir > 1 ? "nt" : "" }} une action.</b> Une vérification dépassée bloque la délivrance des permis pour son porteur.</div>
          </div>

          <div v-for="item in epi.liste" :key="item.id">
            <div
              class="row"
              :style="etat(item).tag === 't-red' ? 'border-color:#F5C6C2' : ''"
              :role="peutVerifier ? 'button' : undefined"
              :tabindex="peutVerifier ? 0 : undefined"
              @click="peutVerifier && basculerAction(item)"
              @keydown.enter="peutVerifier && basculerAction(item)"
            >
              <span class="lead" :class="etat(item).lead"><Icone :nom="etat(item).icone" /></span>
              <div class="tx">
                <b>{{ item.numero }} · {{ LIBELLES_TYPE[item.type] ?? item.type }}</b>
                <div class="meta">
                  <span>{{ item.porteur_id ? epi.nomUtilisateur(item.porteur_id) ?? `Utilisateur #${item.porteur_id}` : "Non affecté" }}</span>
                  <span v-if="item.statut === 'reforme'">Réformé{{ item.motif_reforme ? ` — ${item.motif_reforme}` : "" }}</span>
                  <span v-else>Prochaine vérification {{ formaterDate(item.prochaine_verification) }}</span>
                </div>
              </div>
              <span class="tag" :class="etat(item).tag">{{ etat(item).libelle }}</span>
            </div>
            <div v-if="epiEnAction === item.id" class="card" style="padding: 11px; margin: -4px 0 10px">
              <div class="btnrow">
                <button class="btn pri sm" style="width: auto" @click.stop="verifier(item, true)">Conforme</button>
                <button class="btn gh sm" style="width: auto" @click.stop="verifier(item, false)">Non conforme</button>
              </div>
            </div>
          </div>

          <div v-if="!epi.chargement && !epi.liste.length" class="empty">
            <div class="ic"><Icone nom="shield" taille="lg" /></div>
            <b>Aucun EPI enregistré</b>
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

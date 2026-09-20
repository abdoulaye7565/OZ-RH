<script setup>
/**
 * Écran SLAM mobile — maquette #s-slam (figure A.5 du CDC). Les 4 étapes et
 * leurs points sont chargés depuis GET /slam/referentiel (backend, prompt
 * 2.2) : le contenu n'est jamais dupliqué en dur ici.
 *
 * Écarts assumés, détaillés dans docs/JOURNAL.md :
 * - Bandeau d'intervention de la maquette ("Pylône 24 m — FASO-NET, permis
 *   2026-041...") remplacé par un rappel générique : SLAM n'est pas relié à
 *   un permis précis dans notre modèle (décision actée au prompt 2.2, la
 *   correspondance se fait par la date du jour, pas par une clé étrangère).
 * - Accès au plan de sauvetage ajouté (PlanSauvetage.vue) : absent de la
 *   maquette, mais explicitement demandé par ce prompt.
 * Mode hors connexion (2026-09-09, voir docs/JOURNAL.md "Points critiques"
 * point 4) : deux volets, parce que cet écran a un besoin que Signalements
 * n'a pas — un référentiel à LIRE avant de pouvoir rien saisir.
 * - Lecture : le référentiel (GET /slam/referentiel) est mis en cache dans
 *   localStorage dès qu'il charge avec succès ; si le réseau manque au
 *   chargement, l'écran retombe sur ce cache plutôt que d'afficher une
 *   erreur bloquante — sauf la toute première fois, jamais mis en cache,
 *   où rien ne permet de faire autrement (limite réelle, assumée).
 * - Écriture : la décision GO/NO_GO part en file (stores/horsConnexion.js,
 *   même mécanisme que Signalements) si le réseau manque à l'envoi — cette
 *   décision est celle qui autorise ou non l'intervention (CLAUDE.md
 *   §7.2), elle doit rester utilisable même sans réseau, pas seulement
 *   silencieusement dégradée.
 */
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import Icone from "../components/Icone.vue";
import BandeauReseau from "../components/BandeauReseau.vue";
import PlanSauvetage from "../components/PlanSauvetage.vue";
import api from "../services/api";
import { useHorsConnexionStore } from "../stores/horsConnexion";

const CLE_CACHE_REFERENTIEL = "sheq_slam_referentiel_cache";

const router = useRouter();
const horsConnexion = useHorsConnexionStore();

const etapes = ref([]);
const etapeCourante = ref(0);
const pointsCoches = ref([]); // tableau de tableaux de booléens
const decision = ref(null); // null | "GO" | "NO_GO"
const enAttenteSynchro = ref(false);
const motifNoGo = ref("");
const erreur = ref(null);
const envoiEnCours = ref(false);
const chargement = ref(true);

function lireCacheReferentiel() {
  try {
    const brut = localStorage.getItem(CLE_CACHE_REFERENTIEL);
    return brut ? JSON.parse(brut) : null;
  } catch {
    return null;
  }
}

function ecrireCacheReferentiel(valeur) {
  try {
    localStorage.setItem(CLE_CACHE_REFERENTIEL, JSON.stringify(valeur));
  } catch {
    // Stockage indisponible : le cache ne survit simplement pas, pas bloquant.
  }
}

onMounted(async () => {
  try {
    etapes.value = await api.requete("/api/v1/slam/referentiel");
    ecrireCacheReferentiel(etapes.value);
  } catch (e) {
    const cache = lireCacheReferentiel();
    if (e instanceof TypeError && cache) {
      etapes.value = cache;
    } else {
      erreur.value = "Impossible de charger le référentiel SLAM";
    }
  } finally {
    pointsCoches.value = etapes.value.map((e) => e.points.map(() => false));
    chargement.value = false;
  }
});

const etape = computed(() => etapes.value[etapeCourante.value]);
const derniereEtape = computed(() => etapeCourante.value === etapes.value.length - 1);
const touteLetapeValidee = computed(
  () => pointsCoches.value[etapeCourante.value]?.every(Boolean) ?? false
);

function basculerPoint(index) {
  pointsCoches.value[etapeCourante.value][index] = !pointsCoches.value[etapeCourante.value][index];
}

function etapeSuivante() {
  if (!touteLetapeValidee.value || derniereEtape.value) return;
  etapeCourante.value += 1;
}

async function enregistrerDecision(choix) {
  if (choix === "NO_GO" && !motifNoGo.value.trim()) {
    erreur.value = "Un motif est obligatoire pour un NO GO";
    return;
  }
  envoiEnCours.value = true;
  erreur.value = null;
  const champs = {
    etapes_validees: pointsCoches.value,
    decision: choix,
    motif: choix === "NO_GO" ? motifNoGo.value.trim() : null,
  };
  try {
    await api.requete("/api/v1/slam", { methode: "POST", corps: champs });
    decision.value = choix;
  } catch (e) {
    if (e instanceof TypeError) {
      // Pas de réseau : la décision est actée localement tout de suite (elle
      // conditionne l'intervention, CLAUDE.md §7.2) et repartira d'elle-même
      // au retour du réseau (stores/horsConnexion.js) — jamais perdue.
      await horsConnexion.ajouterEnAttente("slam", champs, []);
      decision.value = choix;
      enAttenteSynchro.value = true;
    } else {
      erreur.value = e instanceof api.ErreurApi ? e.message : "Envoi impossible, réessayez";
    }
  } finally {
    envoiEnCours.value = false;
  }
}

const messageVerdict = computed(() =>
  decision.value === "GO"
    ? "GO enregistré. Bonne intervention — restez ancré à 100 %. Le responsable est notifié."
    : "NO GO enregistré. Vous avez bien fait : l'intervention est reportée et le responsable prévenu."
);
</script>

<template>
  <div class="ecran-mobile">
    <BandeauReseau />

    <div v-if="chargement" class="pad"><div class="skel" style="height: 140px"></div></div>

    <template v-else-if="!decision">
      <div class="slam">
        <div class="top">
          <div class="lt">{{ etape.lettre }}</div>
          <div>
            <h2>{{ etape.titre }}</h2>
            <div class="s">{{ etape.sous_titre }}</div>
          </div>
          <div class="cnt">{{ etapeCourante + 1 }}/{{ etapes.length }}</div>
        </div>
        <div class="prog">
          <div v-for="(e, i) in etapes" :key="i" class="st" :class="{ on: i <= etapeCourante }"></div>
        </div>
      </div>

      <div class="body">
        <div class="pad">
          <ul class="cl">
            <li
              v-for="(point, i) in etape.points"
              :key="i"
              :class="{ ok: pointsCoches[etapeCourante][i] }"
              @click="basculerPoint(i)"
            >
              <span class="cb"><Icone v-if="pointsCoches[etapeCourante][i]" nom="check" taille="sm" /></span>
              <span class="tx">{{ point }}</span>
            </li>
          </ul>

          <button
            v-if="!derniereEtape"
            class="btn pri"
            :disabled="!touteLetapeValidee"
            @click="etapeSuivante"
          >
            Étape suivante
            <Icone nom="chev" taille="sm" />
          </button>

          <template v-else>
            <div v-if="!touteLetapeValidee">
              <label class="f" for="motif-no-go">Motif (obligatoire pour NO GO)</label>
              <textarea id="motif-no-go" v-model="motifNoGo" class="inp" placeholder="Ex. vent trop fort"></textarea>
            </div>
            <div class="btnrow" style="margin-top: 12px">
              <button class="btn go" :disabled="!touteLetapeValidee || envoiEnCours" @click="enregistrerDecision('GO')">
                <Icone nom="check" />GO
              </button>
              <button class="btn no" :disabled="envoiEnCours" @click="enregistrerDecision('NO_GO')">
                <Icone nom="x" />NO GO
              </button>
            </div>
          </template>

          <div v-if="erreur" class="banner err" style="margin-top: 12px">{{ erreur }}</div>

          <PlanSauvetage style="margin-top: 14px" />

          <div class="banner info" style="margin-top: 12px">
            <Icone nom="sync" taille="sm" style="margin-top: 1px" />
            <div>
              En cas de coupure réseau, votre décision GO/NO GO est actée immédiatement et
              part automatiquement dès le retour de la connexion.
            </div>
          </div>
        </div>
      </div>
    </template>

    <template v-else>
      <div class="body">
        <div class="pad">
          <div class="verdict show" :class="decision === 'GO' ? 'g' : 'n'">
            <Icone :nom="decision === 'GO' ? 'check' : 'x'" taille="sm" style="margin-top: 1px" />
            <span>{{ messageVerdict }}</span>
          </div>
          <div v-if="enAttenteSynchro" class="banner info" style="margin-top: 10px">
            <Icone nom="sync" taille="sm" style="margin-top: 1px" />
            <div>Enregistrée localement, en attente du retour du réseau pour être synchronisée.</div>
          </div>
          <PlanSauvetage style="margin-top: 14px" />
          <button class="btn gh" style="margin-top: 14px" @click="router.push({ name: 'accueil' })">
            Retour à l'accueil
          </button>
        </div>
      </div>
    </template>

    <nav class="tabs">
      <button class="tb" @click="router.push({ name: 'accueil' })"><Icone nom="home" />Accueil</button>
      <button class="tb" @click="router.push({ name: 'signalements' })"><Icone nom="alert" />Signaux</button>
      <button class="tb on"><Icone nom="climb" />SLAM</button>
      <button class="tb" @click="router.push({ name: 'tableau-de-bord' })"><Icone nom="chart" />Tableau</button>
      <button class="tb" @click="router.push({ name: 'assistant-documentaire' })"><Icone nom="chat" />Assistant</button>
      <button class="tb" @click="router.push({ name: 'menu' })"><Icone nom="grid" />Menu</button>
    </nav>
  </div>
</template>

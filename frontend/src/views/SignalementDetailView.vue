<script setup>
/**
 * Signalement — fiche détail (maquette #p-detail, adaptée).
 *
 * Écart assumé (2026-09-19, revue de compatibilité front/back — "tu corriges
 * tout") : la maquette desktop montre un tableau de causes 5M et un
 * historique/timeline détaillé. `Signalement.causes` est un simple champ
 * texte libre qu'aucune route ne permet encore de renseigner, et aucun
 * modèle de données ne trace l'historique des changements de statut — on
 * n'invente ni l'un ni l'autre ici. Cette fiche affiche uniquement ce que
 * les données réelles supportent : identification, description, photos,
 * et les actions de traitement (PATCH /statut, POST /archiver) qui
 * existaient côté serveur depuis le tout premier prompt sans jamais avoir
 * été câblées à un écran.
 */
import { computed, onMounted, onUnmounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import Icone from "../components/Icone.vue";
import BandeauReseau from "../components/BandeauReseau.vue";
import ModalConfirmation from "../components/ModalConfirmation.vue";
import { useSignalementsStore } from "../stores/signalements";
import { useAuthStore } from "../stores/auth";
import { telechargerPdf } from "../utils/telechargement";
import api from "../services/api";

const route = useRoute();
const router = useRouter();
const signalements = useSignalementsStore();
const auth = useAuthStore();

const signalement = ref(null);
const chargement = ref(true);
const erreur = ref(null);
const actionEnCours = ref(false);
const pdfEnCours = ref(false);
const confirmationArchivage = ref(false);

// Rôles habilités à traiter (Permissions.TRAITER_SIGNALEMENTS côté serveur,
// backend/app/core/permissions.py) : réplique volontairement minimale plutôt
// que d'introduire une dépendance au store des rôles pour ce seul écran (même
// principe que les gardes locales de MenuView.vue).
const ROLES_TRAITEMENT = ["referent_sheq", "administrateur"];
const peutTraiter = computed(() => ROLES_TRAITEMENT.includes(auth.utilisateur?.role));

const LIBELLE_TYPE = {
  situation_dangereuse: "Situation dangereuse",
  presque_accident: "Presque-accident",
  anomalie: "Anomalie matérielle",
  incident: "Incident",
  accident: "Accident",
};

const STYLE_STATUT = {
  nouveau: { tag: "t-red", libelle: "NOUVEAU" },
  en_analyse: { tag: "t-gd", libelle: "EN ANALYSE" },
  actions_definies: { tag: "t-bl", libelle: "ACTIONS DÉFINIES" },
  cloture: { tag: "t-gr", libelle: "CLÔTURÉ" },
};

// Transitions autorisées, reflet de TRANSITIONS_AUTORISEES
// (app/services/signalement_service.py) — le bouton proposé dépend
// uniquement du statut courant, le serveur revalide de toute façon.
const PROCHAINES_ETAPES = {
  nouveau: [{ statut: "en_analyse", libelle: "Prendre en charge" }],
  en_analyse: [
    { statut: "actions_definies", libelle: "Marquer les actions définies" },
    { statut: "cloture", libelle: "Clôturer directement" },
  ],
  actions_definies: [{ statut: "cloture", libelle: "Clôturer" }],
  cloture: [],
};

// `date_constat` est un véritable horodatage (avec fuseau), pas une simple
// date civile : converti en heure locale, comme `date_saisie` dans
// SignalementsView.vue (voir la mise en garde de utils/dates.js).
function formaterDate(iso) {
  return new Date(iso).toLocaleDateString("fr-FR", { day: "2-digit", month: "2-digit", year: "numeric", hour: "2-digit", minute: "2-digit" });
}

const urlsPhotos = ref([]);

function revoquerPhotos() {
  for (const url of urlsPhotos.value) URL.revokeObjectURL(url);
  urlsPhotos.value = [];
}

async function chargerPhotos() {
  revoquerPhotos();
  if (!signalement.value?.photos?.length) return;
  const urls = [];
  for (let i = 0; i < signalement.value.photos.length; i += 1) {
    try {
      const reponse = await api.requete(`/api/v1/signalements/${signalement.value.id}/photos/${i}`, { brut: true });
      urls.push(URL.createObjectURL(await reponse.blob()));
    } catch {
      // Une photo illisible ne doit pas bloquer l'affichage des autres.
    }
  }
  urlsPhotos.value = urls;
}

async function charger() {
  chargement.value = true;
  erreur.value = null;
  try {
    signalement.value = await signalements.obtenir(route.params.id);
    await chargerPhotos();
  } catch (e) {
    erreur.value = e?.message ?? "Impossible de charger ce signalement";
  } finally {
    chargement.value = false;
  }
}

onMounted(charger);
onUnmounted(revoquerPhotos);

async function changerStatut(statut) {
  actionEnCours.value = true;
  erreur.value = null;
  try {
    signalement.value = await signalements.changerStatut(signalement.value.id, statut);
  } catch (e) {
    erreur.value = e?.message ?? "Impossible de mettre à jour le statut";
  } finally {
    actionEnCours.value = false;
  }
}

async function confirmerArchivage() {
  confirmationArchivage.value = false;
  actionEnCours.value = true;
  erreur.value = null;
  try {
    await signalements.archiver(signalement.value.id);
    router.push({ name: "signalements" });
  } catch (e) {
    erreur.value = e?.message ?? "Impossible d'archiver ce signalement";
    actionEnCours.value = false;
  }
}

async function telecharger() {
  pdfEnCours.value = true;
  try {
    await telechargerPdf(
      `/api/v1/signalements/${signalement.value.id}/export-pdf`,
      `${signalement.value.reference ?? "signalement-" + signalement.value.id}.pdf`
    );
  } catch (e) {
    erreur.value = e?.message ?? "Téléchargement du PDF impossible";
  } finally {
    pdfEnCours.value = false;
  }
}
</script>

<template>
  <div class="ecran-mobile">
    <BandeauReseau />
    <header class="hd">
      <button class="back" aria-label="Retour" @click="router.push({ name: 'signalements' })"><Icone nom="back" /></button>
      <div>
        <h1>{{ signalement?.reference ?? "Signalement" }}</h1>
        <div v-if="signalement" class="sub">{{ LIBELLE_TYPE[signalement.type] ?? signalement.type }}</div>
      </div>
    </header>

    <div class="body">
      <div class="pad">
        <div v-if="chargement" class="skel" style="height: 200px"></div>

        <div v-else-if="!signalement" class="banner err">{{ erreur ?? "Signalement introuvable" }}</div>

        <template v-else>
          <div class="card" style="padding: 12px">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px">
              <span class="tag" :class="STYLE_STATUT[signalement.statut]?.tag">{{ STYLE_STATUT[signalement.statut]?.libelle }}</span>
              <button class="btn gh sm" style="width: auto" :disabled="pdfEnCours" @click="telecharger">
                <Icone nom="dl" taille="sm" />PDF
              </button>
            </div>
            <b style="display: block; margin-bottom: 4px">{{ signalement.lieu }}</b>
            <p style="font-size: 13px; color: var(--ink); white-space: pre-wrap">{{ signalement.description }}</p>
            <div class="meta" style="margin-top: 10px">
              <span>{{ signalement.site_nom ?? `Site #${signalement.site_id}` }}</span>
              <span>Constaté le {{ formaterDate(signalement.date_constat) }}</span>
              <span>{{ signalement.anonyme ? "Anonyme" : (signalement.auteur_nom ?? "Auteur inconnu") }}</span>
            </div>
          </div>

          <template v-if="signalement.photos?.length">
            <div class="sec" style="margin-top: 14px">PHOTOS</div>
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px">
              <img
                v-for="(url, i) in urlsPhotos"
                :key="i"
                :src="url"
                alt=""
                style="width: 100%; aspect-ratio: 1; object-fit: cover; border-radius: 8px; border: 1px solid var(--line)"
              />
            </div>
          </template>

          <div v-if="erreur" class="banner err" style="margin-top: 14px">{{ erreur }}</div>

          <template v-if="peutTraiter && signalement.statut !== 'cloture'">
            <div class="sec" style="margin-top: 14px">TRAITEMENT</div>
            <button
              v-for="etape in PROCHAINES_ETAPES[signalement.statut]"
              :key="etape.statut"
              class="btn pri"
              style="margin-top: 8px"
              :disabled="actionEnCours"
              @click="changerStatut(etape.statut)"
            >
              {{ etape.libelle }}
            </button>
          </template>

          <button
            v-if="peutTraiter && signalement.statut === 'cloture'"
            class="btn gh"
            style="margin-top: 14px"
            :disabled="actionEnCours"
            @click="confirmationArchivage = true"
          >
            <Icone nom="inbox" taille="sm" />Archiver
          </button>

          <div style="height: 20px"></div>
        </template>
      </div>
    </div>

    <ModalConfirmation
      v-if="confirmationArchivage"
      titre="Archiver ce signalement"
      message="Il n'apparaîtra plus dans la liste courante. Cette action n'est pas une suppression : la fiche reste consultable en base."
      libelle-confirmer="Archiver"
      @confirmer="confirmerArchivage"
      @annuler="confirmationArchivage = false"
    />
  </div>
</template>

<script setup>
/**
 * Écran "Nouveau signalement" — maquette docs/maquettes/Maquettes_SHEQ_Management_v2.html,
 * section #s-newsig (figure A.3 du CDC).
 *
 * Écarts assumés par rapport à la maquette, faute de champ prévu pour ça dans
 * son formulaire :
 * - `site_id` : pas de sélecteur de site dans la maquette (elle ne montre que
 *   "Lieu", un champ texte libre). Utilisé à la place : le site de rattachement
 *   du compte connecté (auth.utilisateur.site_id) — cohérent avec l'objectif de
 *   saisie en moins de deux minutes, mais à confirmer : un technicien qui
 *   intervient sur le site d'un client différent de son site de rattachement ne
 *   peut pas le signaler ici.
 * - `date_constat` : pas de sélecteur de date/heure non plus ; fixée à l'instant
 *   de l'envoi.
 *
 * Le type n'affiche que les 3 valeurs de la maquette (situation dangereuse,
 * presque-accident, anomalie matérielle), alors que l'API en accepte 5
 * (dictionnaire du CDC, chapitre 7.2.3, ajoute incident et accident). Respecté
 * ici à la lettre de la maquette ("respecte-les : contenu…") — mais cela
 * signifie qu'un accident ne peut pas être déclaré depuis cet écran. À trancher :
 * la maquette est-elle incomplète, ou ces déclarations passent-elles par un
 * autre circuit ?
 */
import { computed, ref } from "vue";
import { useRouter } from "vue-router";
import Icone from "../components/Icone.vue";
import BandeauReseau from "../components/BandeauReseau.vue";
import { useAuthStore } from "../stores/auth";
import { useSignalementsStore } from "../stores/signalements";
import api from "../services/api";

const router = useRouter();
const auth = useAuthStore();
const signalements = useSignalementsStore();

const TYPES = [
  { valeur: "situation_dangereuse", libelle: "Situation dangereuse" },
  { valeur: "presque_accident", libelle: "Presque-accident" },
  { valeur: "anomalie", libelle: "Anomalie matérielle" },
];
const NOMBRE_MAX_PHOTOS = 5;

const type = ref(TYPES[0].valeur);
const lieu = ref("");
const description = ref("");
const anonyme = ref(false);
const photos = ref([]);
const erreurs = ref({});
const erreurServeur = ref(null);
const inputFichier = ref(null);

const previsualisations = computed(() => photos.value.map((f) => URL.createObjectURL(f)));

function ouvrirSelecteurPhoto() {
  inputFichier.value?.click();
}

function ajouterPhotos(evenement) {
  const fichiers = Array.from(evenement.target.files ?? []);
  photos.value = [...photos.value, ...fichiers].slice(0, NOMBRE_MAX_PHOTOS);
  evenement.target.value = "";
}

function retirerPhoto(index) {
  photos.value = photos.value.filter((_, i) => i !== index);
}

function valider() {
  const e = {};
  if (!lieu.value.trim()) e.lieu = "Le lieu est obligatoire";
  if (!description.value.trim()) e.description = "La description est obligatoire";
  // Validation de confort côté client : la validation qui compte reste celle du
  // serveur, réappliquée systématiquement (CLAUDE.md, point 9).
  erreurs.value = e;
  return Object.keys(e).length === 0;
}

async function envoyer() {
  erreurServeur.value = null;
  if (!valider()) return;

  try {
    await signalements.creer(
      {
        type: type.value,
        site_id: auth.utilisateur?.site_id ?? "",
        lieu: lieu.value,
        description: description.value,
        anonyme: anonyme.value,
        date_constat: new Date().toISOString(),
      },
      photos.value
    );
    router.push({ name: "signalements" });
  } catch (e) {
    erreurServeur.value = e instanceof api.ErreurApi ? e.message : "Envoi impossible, réessayez";
  }
}
</script>

<template>
  <div class="ecran-mobile">
    <BandeauReseau />
    <header class="hd">
      <button class="back" aria-label="Retour" @click="router.back()"><Icone nom="back" /></button>
      <div>
        <h1>Nouveau signalement</h1>
        <div class="sub">Deux minutes suffisent</div>
      </div>
    </header>

    <div class="body">
      <div class="pad">
        <label class="f">Type</label>
        <div class="segs">
          <button
            v-for="t in TYPES"
            :key="t.valeur"
            type="button"
            class="seg"
            :class="{ on: type === t.valeur }"
            @click="type = t.valeur"
          >
            {{ t.libelle }}
          </button>
        </div>

        <label class="f" for="lieu">Lieu</label>
        <input
          id="lieu"
          v-model="lieu"
          class="inp"
          :class="{ 'champ-erreur': erreurs.lieu }"
          placeholder="Local technique, pylône, site client…"
        />
        <div v-if="erreurs.lieu" class="msg-erreur">{{ erreurs.lieu }}</div>

        <label class="f" for="description">Description</label>
        <textarea
          id="description"
          v-model="description"
          class="inp"
          :class="{ 'champ-erreur': erreurs.description }"
          placeholder="Que s'est-il passé ? Où ? Comment ?"
        ></textarea>
        <div v-if="erreurs.description" class="msg-erreur">{{ erreurs.description }}</div>

        <label class="f">Photo</label>
        <div class="drop" @click="ouvrirSelecteurPhoto">
          <Icone nom="cam" taille="lg" />
          Prendre une photo
          <input
            ref="inputFichier"
            type="file"
            accept="image/jpeg,image/png,image/webp"
            capture="environment"
            multiple
            @change="ajouterPhotos"
          />
        </div>
        <div v-if="photos.length" class="miniatures">
          <div v-for="(src, i) in previsualisations" :key="i" style="position: relative">
            <img :src="src" :alt="`Photo ${i + 1}`" />
            <button
              type="button"
              class="tag t-red"
              style="position: absolute; top: -6px; right: -6px; padding: 2px 5px"
              aria-label="Retirer cette photo"
              @click="retirerPhoto(i)"
            >
              <Icone nom="x" taille="sm" />
            </button>
          </div>
        </div>

        <div class="switch">
          <div class="tx">
            <b>Envoyer anonymement</b>
            <span>Votre nom ne sera pas enregistré</span>
          </div>
          <button
            type="button"
            class="tg"
            :class="{ on: anonyme }"
            aria-label="Anonyme"
            @click="anonyme = !anonyme"
          ></button>
        </div>

        <div style="height: 14px"></div>

        <div v-if="erreurServeur" class="banner err">{{ erreurServeur }}</div>

        <button class="btn gold" :disabled="signalements.envoiEnCours" @click="envoyer">
          <Icone nom="check" taille="sm" />
          {{ signalements.envoiEnCours ? "Envoi…" : "Envoyer le signalement" }}
        </button>

        <div class="banner warn" style="margin-top: 12px">
          <Icone nom="wifioff" taille="sm" style="margin-top: 1px" />
          <div>
            Le mode hors connexion complet (conservation sur l'appareil et envoi automatique au
            retour du réseau) n'est pas encore actif — il arrive au prompt suivant. Pour l'instant,
            une connexion est nécessaire pour envoyer ce signalement.
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

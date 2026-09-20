<script setup>
/**
 * Dépôt de la photo de profil (2026-09-10, retour direct de l'utilisateur —
 * "permettre à l'utilisateur d'insérer sa photo"). Toujours en
 * libre-service sur son propre compte — pas de sélection d'utilisateur ici,
 * `useAuthStore` connaît déjà "moi".
 *
 * Utilisée à la fois par GestionLayout.vue (desktop, clic sur l'avatar) et
 * MenuView.vue (mobile, section COMPTE) — un seul composant, pas de
 * duplication du formulaire entre les deux interfaces.
 */
import { computed, ref } from "vue";
import Icone from "./Icone.vue";
import Modal from "./Modal.vue";
import { useAuthStore } from "../stores/auth";
import { useAvatar } from "../composables/useAvatar";

const emit = defineEmits(["fermer"]);
const auth = useAuthStore();

const idUtilisateur = computed(() => auth.utilisateur?.id ?? null);
const cheminPhoto = computed(() => auth.utilisateur?.photo ?? null);
const { url: urlPhotoActuelle } = useAvatar(idUtilisateur, cheminPhoto);

const fichierChoisi = ref(null);
const apercu = ref(null); // URL objet de l'aperçu AVANT enregistrement, distincte de urlPhotoActuelle
const inputFichier = ref(null);
const enregistrement = ref(false);
const erreur = ref(null);

const initiales = computed(() => {
  const u = auth.utilisateur;
  if (!u) return "";
  return `${u.prenom?.[0] ?? ""}${u.nom?.[0] ?? ""}`.toUpperCase();
});

function ouvrirSelecteur() {
  inputFichier.value?.click();
}

function surFichierChoisi(e) {
  const fichier = e.target.files?.[0];
  if (!fichier) return;
  fichierChoisi.value = fichier;
  if (apercu.value) URL.revokeObjectURL(apercu.value);
  apercu.value = URL.createObjectURL(fichier);
  erreur.value = null;
}

async function enregistrer() {
  if (!fichierChoisi.value) return;
  enregistrement.value = true;
  erreur.value = null;
  try {
    await auth.changerPhoto(fichierChoisi.value);
    emit("fermer");
  } catch (e) {
    erreur.value = e?.message ?? "Impossible d'enregistrer cette photo";
  } finally {
    enregistrement.value = false;
  }
}

async function retirer() {
  enregistrement.value = true;
  erreur.value = null;
  try {
    await auth.retirerPhoto();
    emit("fermer");
  } catch (e) {
    erreur.value = e?.message ?? "Impossible de retirer cette photo";
  } finally {
    enregistrement.value = false;
  }
}
</script>

<template>
  <Modal titre="Ma photo de profil" @fermer="emit('fermer')">
    <div style="display: flex; flex-direction: column; align-items: center; gap: 12px">
      <div class="photo-apercu">
        <img v-if="apercu ?? urlPhotoActuelle" :src="apercu ?? urlPhotoActuelle" alt="Photo de profil" />
        <span v-else>{{ initiales }}</span>
      </div>

      <input ref="inputFichier" type="file" accept="image/jpeg,image/png,image/webp" style="display: none" @change="surFichierChoisi" />

      <div style="display: flex; gap: 8px">
        <button class="btn gh sm" style="width: auto" @click="ouvrirSelecteur">
          <Icone nom="cam" taille="sm" />{{ urlPhotoActuelle || apercu ? "Changer la photo" : "Choisir une photo" }}
        </button>
        <button v-if="cheminPhoto && !fichierChoisi" class="btn gh sm" style="width: auto" :disabled="enregistrement" @click="retirer">
          Retirer la photo
        </button>
      </div>

      <p class="sub" style="text-align: center; margin: 0">JPEG, PNG ou WebP — 5 Mo maximum.</p>

      <div v-if="erreur" class="banner err" style="width: 100%">{{ erreur }}</div>

      <div style="display: flex; gap: 8px; width: 100%; margin-top: 4px">
        <button class="btn pri" style="width: auto" :disabled="!fichierChoisi || enregistrement" @click="enregistrer">
          Enregistrer
        </button>
        <button class="btn gh" style="width: auto" @click="emit('fermer')">Annuler</button>
      </div>
    </div>
  </Modal>
</template>

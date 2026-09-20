<script setup>
/**
 * Aperçu d'un document (2026-09-09, retour direct de l'utilisateur —
 * "lorsque l'on clique sur un document on doit voir l'aperçu du dit
 * document" : jusqu'ici, "Ouvrir" renvoyait simplement vers un nouvel
 * onglet, sans aperçu dans l'application elle-même).
 *
 * PDF : affiché dans un <iframe> (visionneuse native du navigateur, avec
 * son propre outil d'impression déjà intégré). Image : <img>. Tout autre
 * format : pas de rendu fiable en HTML pur, un lien "Ouvrir dans un nouvel
 * onglet" reste proposé plutôt que de prétendre prévisualiser ce qui ne
 * peut pas l'être.
 *
 * Impression dédiée à CE document (pas à l'écran de l'application, qui a
 * son propre bouton "Imprimer" dans GestionLayout.vue pour les tableaux/
 * fiches) : ouvre le fichier dans une fenêtre séparée puis y déclenche
 * l'impression — fonctionne pour tous les types, contrairement à
 * iframe.contentWindow.print() qui ne s'applique proprement qu'aux PDF.
 */
import { onBeforeUnmount, onMounted, ref } from "vue";
import Icone from "./Icone.vue";
import Modal from "./Modal.vue";
import api from "../services/api";

const props = defineProps({
  documentId: { type: [Number, String], required: true },
  titre: { type: String, default: "Aperçu du document" },
  nomFichier: { type: String, default: "" },
});
const emit = defineEmits(["fermer"]);

const EXTENSIONS_IMAGE = new Set([".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".svg"]);

const chargement = ref(true);
const erreur = ref(null);
const url = ref(null);
const type = ref(null); // "pdf" | "image" | "autre"

function extensionDe(nom) {
  const i = nom.lastIndexOf(".");
  return i === -1 ? "" : nom.slice(i).toLowerCase();
}

onMounted(async () => {
  try {
    const reponse = await api.requete(`/api/v1/documents/${props.documentId}/fichier`, { brut: true });
    const blob = await reponse.blob();
    url.value = URL.createObjectURL(blob);
    const extension = extensionDe(props.nomFichier);
    if (extension === ".pdf" || blob.type === "application/pdf") type.value = "pdf";
    else if (EXTENSIONS_IMAGE.has(extension) || blob.type.startsWith("image/")) type.value = "image";
    else type.value = "autre";
  } catch (e) {
    erreur.value = e instanceof api.ErreurApi ? e.message : "Impossible de charger ce document";
  } finally {
    chargement.value = false;
  }
});

onBeforeUnmount(() => {
  if (url.value) URL.revokeObjectURL(url.value);
});

function imprimer() {
  const fenetre = window.open(url.value, "_blank");
  if (!fenetre) return; // bloqueur de fenêtres pop-up : rien à faire de plus, le lien "ouvrir" reste disponible
  fenetre.addEventListener("load", () => fenetre.print());
}
</script>

<template>
  <Modal :titre="titre" @fermer="emit('fermer')">
    <div v-if="chargement" style="padding: 24px; text-align: center; color: var(--mut)">Chargement de l'aperçu…</div>
    <div v-else-if="erreur" class="banner err">{{ erreur }}</div>
    <template v-else>
      <iframe
        v-if="type === 'pdf'"
        :src="url"
        title="Aperçu du document"
        style="width: 100%; height: 70vh; border: 1px solid var(--line); border-radius: var(--r)"
      ></iframe>
      <img v-else-if="type === 'image'" :src="url" alt="Aperçu du document" style="max-width: 100%; border-radius: var(--r); display: block; margin: 0 auto" />
      <div v-else class="banner info">
        <Icone nom="doc" taille="sm" style="margin-top: 1px" />
        <div>Ce type de fichier ne peut pas être prévisualisé directement ici — ouvrez-le dans un nouvel onglet.</div>
      </div>

      <div style="display: flex; gap: 8px; margin-top: 12px">
        <button class="btn pri" style="width: auto" @click="imprimer"><Icone nom="print" taille="sm" />Imprimer</button>
        <a
          class="btn gh"
          style="width: auto; text-decoration: none; display: inline-flex; align-items: center; justify-content: center; gap: 6px"
          :href="url"
          target="_blank"
          rel="noopener"
        >
          Ouvrir dans un nouvel onglet
        </a>
      </div>
    </template>
  </Modal>
</template>

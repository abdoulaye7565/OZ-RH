<script setup>
/**
 * Assistant documentaire — vue mobile (prompt 6.2, chapitre 16.2.1 du CDC).
 *
 * Aucune maquette de référence pour cet écran (fonctionnalité ajoutée après les
 * 41 écrans de référence, lot 6 hors périmètre initial) : structure calquée sur
 * NouveauSignalementView (champ de saisie unique, retour direct) plutôt
 * qu'inventée sans repère.
 */
import { ref } from "vue";
import { useRouter } from "vue-router";
import Icone from "../components/Icone.vue";
import BandeauReseau from "../components/BandeauReseau.vue";
import api from "../services/api";
import { useAssistantDocumentaireStore } from "../stores/assistantDocumentaire";

const router = useRouter();
const assistant = useAssistantDocumentaireStore();
const saisie = ref("");

function envoyer() {
  if (!saisie.value.trim()) return;
  assistant.poser(saisie.value.trim());
}

async function ouvrirDocument(documentId) {
  try {
    const reponse = await api.requete(`/api/v1/documents/${documentId}/fichier`, { brut: true });
    const blob = await reponse.blob();
    window.open(URL.createObjectURL(blob), "_blank");
  } catch {
    // Fichier introuvable ou droits insuffisants : géré silencieusement côté
    // UI, l'utilisateur voit simplement que rien ne s'ouvre — cohérent avec
    // le principe "mode dégradé" du reste du service d'assistance.
  }
}
</script>

<template>
  <div class="ecran-mobile">
    <BandeauReseau />
    <header class="hd">
      <div class="mk">H</div>
      <div>
        <h1>Assistant documentaire</h1>
        <div class="sub">Posez une question sur le système documentaire</div>
      </div>
    </header>

    <div class="wrap">
      <div class="body">
        <div class="pad">
          <div class="card" style="padding: 13px">
            <textarea
              v-model="saisie"
              class="inp"
              rows="3"
              placeholder="Ex. : que faire si le vent se lève pendant une intervention en hauteur ?"
              @keydown.enter.exact.prevent="envoyer"
            ></textarea>
            <div style="height: 10px"></div>
            <button class="btn pri" :disabled="assistant.chargement || !saisie.trim()" @click="envoyer">
              {{ assistant.chargement ? "Recherche…" : "Poser la question" }}
            </button>
          </div>

          <div style="height: 12px"></div>

          <div v-if="assistant.erreur" class="banner err">{{ assistant.erreur }}</div>

          <template v-if="assistant.reponse">
            <div v-if="!assistant.reponse.disponible" class="banner info">
              L'assistant documentaire est indisponible pour le moment. Réessayez plus tard.
            </div>
            <div v-else class="card" style="padding: 13px">
              <div class="sec" style="margin-bottom: 11px">RÉPONSE</div>
              <p style="white-space: pre-wrap">{{ assistant.reponse.reponse }}</p>

              <template v-if="assistant.reponse.reponse_trouvee">
                <div style="height: 10px"></div>
                <div class="sec" style="margin-bottom: 8px">RÉFÉRENCES</div>
                <button
                  v-for="ref in assistant.reponse.references"
                  :key="`${ref.document_id}-${ref.section}`"
                  class="btn gh"
                  style="width: 100%; justify-content: flex-start; margin-bottom: 6px"
                  @click="ouvrirDocument(ref.document_id)"
                >
                  <Icone nom="search" taille="sm" />
                  <span>{{ ref.reference }} — {{ ref.section }}</span>
                </button>
              </template>
            </div>
          </template>

          <div style="height: 56px"></div>
        </div>
      </div>
    </div>

    <nav class="tabs">
      <button class="tb" @click="router.push({ name: 'accueil' })"><Icone nom="home" />Accueil</button>
      <button class="tb" @click="router.push({ name: 'signalements' })"><Icone nom="alert" />Signaux</button>
      <button class="tb" @click="router.push({ name: 'slam' })"><Icone nom="climb" />SLAM</button>
      <button class="tb" @click="router.push({ name: 'tableau-de-bord' })"><Icone nom="chart" />Tableau</button>
      <button class="tb on"><Icone nom="chat" />Assistant</button>
      <button class="tb" @click="router.push({ name: 'menu' })"><Icone nom="grid" />Menu</button>
    </nav>
  </div>
</template>

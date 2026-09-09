<script setup>
/**
 * Assistant documentaire — vue desktop (prompt 6.2). Même écart que
 * TableauBordDesktopView : pas de barre latérale complète, un bandeau simple
 * avec un lien de retour.
 */
import { ref } from "vue";
import Icone from "../components/Icone.vue";
import api from "../services/api";
import { useAssistantDocumentaireStore } from "../stores/assistantDocumentaire";

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
    // Voir AssistantDocumentaireView.vue : géré silencieusement, mode dégradé.
  }
}
</script>

<template>
  <div>
    <div class="card">
      <div class="ch"><Icone nom="chat" /><h3>Poser une question</h3></div>
      <div class="cb">
        <textarea
          v-model="saisie"
          class="inp"
          rows="2"
          placeholder="Ex. : quelle est la procédure après un accident bénin ?"
          @keydown.enter.exact.prevent="envoyer"
        ></textarea>
        <div style="height: 10px"></div>
        <button class="btn pri" style="width: auto" :disabled="assistant.chargement || !saisie.trim()" @click="envoyer">
          {{ assistant.chargement ? "Recherche…" : "Poser la question" }}
        </button>
      </div>
    </div>

    <div v-if="assistant.erreur" class="banner err">{{ assistant.erreur }}</div>

    <template v-if="assistant.reponse">
      <div v-if="!assistant.reponse.disponible" class="banner info">
        L'assistant documentaire est indisponible pour le moment. Réessayez plus tard.
      </div>
      <div v-else class="card">
        <div class="ch"><Icone nom="check" /><h3>Réponse</h3></div>
        <div class="cb">
          <p style="white-space: pre-wrap">{{ assistant.reponse.reponse }}</p>

          <template v-if="assistant.reponse.reponse_trouvee">
            <div style="height: 12px"></div>
            <div class="sec" style="margin-bottom: 8px">Références</div>
            <button
              v-for="ref in assistant.reponse.references"
              :key="`${ref.document_id}-${ref.section}`"
              class="btn gh"
              style="width: auto; margin-right: 8px; margin-bottom: 6px"
              @click="ouvrirDocument(ref.document_id)"
            >
              <Icone nom="search" taille="sm" />
              <span>{{ ref.reference }} — {{ ref.section }}</span>
            </button>
          </template>
        </div>
      </div>
    </template>
  </div>
</template>

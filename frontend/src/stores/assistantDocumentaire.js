import { defineStore } from "pinia";
import api from "../services/api";

export const useAssistantDocumentaireStore = defineStore("assistantDocumentaire", {
  state: () => ({
    question: "",
    reponse: null,
    chargement: false,
    erreur: null,
  }),

  actions: {
    async poser(question) {
      this.chargement = true;
      this.erreur = null;
      this.reponse = null;
      try {
        this.reponse = await api.requete("/api/v1/assistance/question-documentaire", {
          methode: "POST",
          corps: { question },
        });
      } catch (e) {
        this.erreur = e instanceof api.ErreurApi ? e.message : "Impossible d'interroger l'assistant documentaire";
      } finally {
        this.chargement = false;
      }
    },
  },
});

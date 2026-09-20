import { onUnmounted, ref, watch } from "vue";
import api from "../services/api";

/**
 * Charge la photo de profil d'un utilisateur en URL objet affichable
 * (`<img :src>`), sur la même route authentifiée que le reste des pièces
 * jointes de l'app (pas de montage statique, voir ApercuDocument.vue pour
 * le même principe côté documents) — 2026-09-10, retour direct de
 * l'utilisateur ("insérer sa photo").
 *
 * @param {import('vue').Ref<number|null|undefined>} utilisateurId
 * @param {import('vue').Ref<string|null|undefined>} cheminPhoto - `utilisateur.photo` ; sert seulement à savoir QUAND recharger (change à chaque dépôt/retrait), jamais utilisé comme URL directe.
 * @returns {{ url: import('vue').Ref<string|null> }}
 */
export function useAvatar(utilisateurId, cheminPhoto) {
  const url = ref(null);

  function revoquer() {
    if (url.value) {
      URL.revokeObjectURL(url.value);
      url.value = null;
    }
  }

  async function charger() {
    revoquer();
    if (!utilisateurId.value || !cheminPhoto.value) return;
    try {
      const reponse = await api.requete(`/api/v1/auth/utilisateurs/${utilisateurId.value}/photo`, { brut: true });
      const blob = await reponse.blob();
      url.value = URL.createObjectURL(blob);
    } catch {
      // Photo introuvable ou réseau indisponible : on retombe sur les
      // initiales (déjà le rendu par défaut), pas d'erreur bloquante pour
      // un simple avatar.
    }
  }

  watch([utilisateurId, cheminPhoto], charger, { immediate: true });
  onUnmounted(revoquer);

  return { url };
}

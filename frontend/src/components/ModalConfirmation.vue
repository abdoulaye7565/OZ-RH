<script setup>
/**
 * Confirmation d'une action sensible (archivage, suppression logique…) —
 * revue d'ensemble 2026-09-10. Remplace `window.confirm()`, incohérent avec
 * le langage visuel de l'app (et impossible à styler/tester).
 *
 * Usage : l'écran garde une ref `confirmation` (null | { ...contexte }),
 * l'ouvre au clic, et câble @confirmer / @annuler.
 *
 *   <ModalConfirmation
 *     v-if="aArchiver"
 *     titre="Archiver le site"
 *     :message="`Archiver « ${aArchiver.nom} » ? Il n'apparaîtra plus dans les listes.`"
 *     libelle-confirmer="Archiver"
 *     @confirmer="archiver(aArchiver)"
 *     @annuler="aArchiver = null"
 *   />
 */
import Modal from "./Modal.vue";

defineProps({
  titre: { type: String, required: true },
  message: { type: String, required: true },
  libelleConfirmer: { type: String, default: "Confirmer" },
  libelleAnnuler: { type: String, default: "Annuler" },
  // "danger" (rouge) par défaut pour une action destructrice ; "pri" sinon.
  variante: { type: String, default: "danger" },
});
const emit = defineEmits(["confirmer", "annuler"]);
</script>

<template>
  <Modal :titre="titre" @fermer="emit('annuler')">
    <p style="margin: 0 0 14px; line-height: 1.5">{{ message }}</p>
    <div style="display: flex; gap: 8px">
      <button
        class="btn"
        :class="variante === 'danger' ? 'gh' : 'pri'"
        :style="variante === 'danger' ? 'width:auto;color:var(--red);border-color:var(--red)' : 'width:auto'"
        @click="emit('confirmer')"
      >
        {{ libelleConfirmer }}
      </button>
      <button class="btn gh" style="width: auto" @click="emit('annuler')">{{ libelleAnnuler }}</button>
    </div>
  </Modal>
</template>

<script setup>
defineProps({
  nom: { type: String, required: true },
  taille: { type: String, default: "" }, // "", "sm", "lg", "xl"
});
</script>

<template>
  <svg class="i" :class="taille"><use :href="`#i-${nom}`" /></svg>
</template>

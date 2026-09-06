<script setup>
/**
 * Sprite d'icônes SVG au trait, repris tel quel des maquettes
 * (docs/maquettes/Maquettes_SHEQ_Management_v2.html) — style Lucide, point 8 de
 * CLAUDE.md. Monté une fois dans App.vue ; les icônes s'utilisent ensuite via
 * <Icone nom="back" />.
 */
</script>

<template>
  <svg style="display: none" aria-hidden="true">
    <symbol id="i-alert" viewBox="0 0 24 24">
      <path d="M12 9v4M12 17h.01M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0Z" />
    </symbol>
    <symbol id="i-home" viewBox="0 0 24 24">
      <path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" /><path d="M9 22V12h6v10" />
    </symbol>
    <symbol id="i-climb" viewBox="0 0 24 24">
      <path d="M12 3v18M7 7l5-4 5 4M7 13l5-4 5 4M7 19l5-4 5 4" />
    </symbol>
    <symbol id="i-antenna" viewBox="0 0 24 24">
      <path d="M12 12v9M5 12a7 7 0 0 1 14 0M2 12a10 10 0 0 1 20 0" /><circle cx="12" cy="12" r="1.6" />
    </symbol>
    <symbol id="i-chart" viewBox="0 0 24 24"><path d="M3 3v18h18" /><path d="M7 15v3M12 10v8M17 6v12" /></symbol>
    <symbol id="i-check" viewBox="0 0 24 24"><path d="m5 12 5 5L20 7" /></symbol>
    <symbol id="i-x" viewBox="0 0 24 24"><path d="M18 6 6 18M6 6l12 12" /></symbol>
    <symbol id="i-back" viewBox="0 0 24 24"><path d="m14 6-6 6 6 6" /></symbol>
    <symbol id="i-chev" viewBox="0 0 24 24"><path d="m9 6 6 6-6 6" /></symbol>
    <symbol id="i-plus" viewBox="0 0 24 24"><path d="M12 5v14M5 12h14" /></symbol>
    <symbol id="i-cam" viewBox="0 0 24 24">
      <path
        d="M3 8a2 2 0 0 1 2-2h2l1.5-2h7L17 6h2a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"
      /><circle cx="12" cy="13" r="3.5" />
    </symbol>
    <symbol id="i-search" viewBox="0 0 24 24"><circle cx="11" cy="11" r="7" /><path d="m20 20-3.5-3.5" /></symbol>
    <symbol id="i-clock" viewBox="0 0 24 24"><circle cx="12" cy="12" r="9" /><path d="M12 7v5l3.5 2" /></symbol>
    <symbol id="i-shield" viewBox="0 0 24 24">
      <path d="M12 2 4 5v6c0 5 3.4 9.4 8 11 4.6-1.6 8-6 8-11V5Z" />
    </symbol>
    <symbol id="i-lock" viewBox="0 0 24 24">
      <rect x="4" y="10" width="16" height="11" rx="2" /><path d="M8 10V7a4 4 0 0 1 8 0v3" />
    </symbol>
    <symbol id="i-wifi" viewBox="0 0 24 24">
      <path d="M5 12.5a10 10 0 0 1 14 0M8.5 16a5 5 0 0 1 7 0M2 9a15 15 0 0 1 20 0" /><path d="M12 20h.01" />
    </symbol>
    <symbol id="i-wifioff" viewBox="0 0 24 24">
      <path
        d="M2 3l19 19M8.5 16a5 5 0 0 1 6.3-.7M5 12.5a10 10 0 0 1 4-2.4M2 9a15 15 0 0 1 5.5-3.4M15 9.5a10 10 0 0 1 4 3M13.5 5.8A15 15 0 0 1 22 9M12 20h.01"
      />
    </symbol>
  </svg>
</template>

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
    <!-- Logo Hirondelles IT Lab. Redessiné le 2026-09-10 d'après l'emblème
         fourni par l'utilisateur (cercle fin + hirondelle vue de face, ailes
         relevées, corps et queue fourchue) : passage d'un tracé au trait à
         une silhouette pleine (`fill` explicite, `stroke` neutralisé sur ce
         seul symbole) — une marque pleine reste lisible dans les pastilles
         .mk de 24-40 px là où un trait fin se perdait. viewBox 0 0 48 48.
         L'utilisateur a fourni un PNG : cette version SVG le reproduit au
         plus près ; pour un rendu strictement identique, déposer le PNG dans
         src/assets/ et l'y référencer. -->
    <symbol id="i-hirondelle" viewBox="0 0 48 48">
      <circle cx="24" cy="24" r="21.4" fill="none" stroke="currentColor" stroke-width="2" />
      <path
        fill="currentColor"
        stroke="none"
        d="M24 26.2c-2.7-3.6-7-6.6-13.6-8.3 3.2 3.9 5.5 7 7.2 10.2-1.9.5-3.9.7-6 .6 3 2.4 6.1 3.6 9.2 3.6l2 8.1 1.2-8.1c3.1 0 6.2-1.2 9.2-3.6-2.1.1-4.1-.1-6-.6 1.7-3.2 4-6.3 7.2-10.2C31 19.6 26.7 22.6 24 26.2Z"
      />
    </symbol>
    <symbol id="i-alert" viewBox="0 0 24 24">
      <path d="M12 9v4M12 17h.01M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0Z" />
    </symbol>
    <!-- Téléchargement (flèche vers le bac) — ajouté 2026-09-10 pour les
         boutons d'export PDF, style trait Lucide comme le reste du jeu. -->
    <symbol id="i-dl" viewBox="0 0 24 24">
      <path d="M12 3v12" /><path d="m7 10 5 5 5-5" /><path d="M5 21h14" />
    </symbol>
    <!-- Déconnexion — ajouté 2026-09-10, aucun bouton de déconnexion volontaire
         n'existait jusqu'ici (voir docs/JOURNAL.md). -->
    <symbol id="i-logout" viewBox="0 0 24 24">
      <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
      <path d="m16 17 5-5-5-5" /><path d="M21 12H9" />
    </symbol>
    <symbol id="i-print" viewBox="0 0 24 24">
      <path d="M6 9V2h12v7" /><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2" />
      <rect x="6" y="14" width="12" height="8" />
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
    <!-- Assistant documentaire (prompt 6.2) : icône bulle de discussion. -->
    <symbol id="i-chat" viewBox="0 0 24 24"><path d="M7.9 20A9 9 0 1 0 4 16.1L2 22Z" /></symbol>
    <!-- Reprises telles quelles de docs/maquettes/Maquettes_SHEQ_Management_v2.html. -->
    <symbol id="i-vest" viewBox="0 0 24 24"><path d="M8 3 4 5v16h16V5l-4-2-4 4Z" /><path d="M12 7v14M4 12h4M16 12h4" /></symbol>
    <symbol id="i-cap" viewBox="0 0 24 24"><path d="m12 4 10 5-10 5L2 9Z" /><path d="M6 11v5c0 1.7 2.7 3 6 3s6-1.3 6-3v-5" /></symbol>
    <symbol id="i-clip" viewBox="0 0 24 24">
      <rect x="5" y="4" width="14" height="18" rx="2" /><path d="M9 4V2.8A.8.8 0 0 1 9.8 2h4.4a.8.8 0 0 1 .8.8V4" /><path d="M9 11h6M9 15h4" />
    </symbol>
    <symbol id="i-grid" viewBox="0 0 24 24">
      <rect x="3" y="3" width="7" height="7" rx="1.5" /><rect x="14" y="3" width="7" height="7" rx="1.5" />
      <rect x="3" y="14" width="7" height="7" rx="1.5" /><rect x="14" y="14" width="7" height="7" rx="1.5" />
    </symbol>
    <symbol id="i-target" viewBox="0 0 24 24"><circle cx="12" cy="12" r="9" /><circle cx="12" cy="12" r="5" /><circle cx="12" cy="12" r="1.4" /></symbol>
    <symbol id="i-list" viewBox="0 0 24 24"><path d="M8 6h13M8 12h13M8 18h13M3.5 6h.01M3.5 12h.01M3.5 18h.01" /></symbol>
    <symbol id="i-doc" viewBox="0 0 24 24"><path d="M14 2H7a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7Z" /><path d="M14 2v5h5M9 13h6M9 17h4" /></symbol>
    <symbol id="i-door" viewBox="0 0 24 24"><path d="M4 21h16M6 21V4a1 1 0 0 1 1-1h9a1 1 0 0 1 1 1v17" /><path d="M13.5 12h.01" /></symbol>
    <symbol id="i-recycle" viewBox="0 0 24 24">
      <path d="m7 19-3-5 3-2M4.5 14h6.5l3-5M17 19l3-5-4.5.5M20 14l-3.2-5.5-5.3.5M9 4.5 6 9.5l5 .5" />
    </symbol>
    <symbol id="i-star" viewBox="0 0 24 24"><path d="m12 3 2.9 5.9 6.5.9-4.7 4.6 1.1 6.4-5.8-3-5.8 3 1.1-6.4L2.6 9.8l6.5-.9Z" /></symbol>
    <symbol id="i-bell" viewBox="0 0 24 24"><path d="M18 8a6 6 0 1 0-12 0c0 6-3 7-3 7h18s-3-1-3-7" /><path d="M10.5 21a2 2 0 0 0 3 0" /></symbol>
    <symbol id="i-file" viewBox="0 0 24 24"><path d="M3 7a2 2 0 0 1 2-2h5l2 2h7a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" /></symbol>
    <symbol id="i-key" viewBox="0 0 24 24"><circle cx="8" cy="15" r="4" /><path d="m10.8 12.2 8.2-8.2M17 6l2.5 2.5M14.5 8.5 17 11" /></symbol>
    <symbol id="i-inbox" viewBox="0 0 24 24"><path d="M3 12h5l2 3h4l2-3h5" /><path d="M5.5 5h13l2.5 7v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-7Z" /></symbol>
    <symbol id="i-eye" viewBox="0 0 24 24"><path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7-10-7-10-7Z" /><circle cx="12" cy="12" r="3" /></symbol>
    <symbol id="i-sync" viewBox="0 0 24 24"><path d="M3 12a9 9 0 0 1 15-6.7L21 8" /><path d="M21 3v5h-5M21 12a9 9 0 0 1-15 6.7L3 16" /><path d="M3 21v-5h5" /></symbol>
    <symbol id="i-users" viewBox="0 0 24 24">
      <circle cx="9" cy="8" r="3.5" /><path d="M2.5 20a6.5 6.5 0 0 1 13 0" /><path d="M16 5.2a3.5 3.5 0 0 1 0 5.6M18 14.4a6.5 6.5 0 0 1 3.5 5.6" />
    </symbol>
    <symbol id="i-calendar" viewBox="0 0 24 24">
      <rect x="3" y="5" width="18" height="16" rx="2" /><path d="M8 3v4M16 3v4M3 10h18" />
    </symbol>
    <symbol id="i-cog" viewBox="0 0 24 24">
      <circle cx="12" cy="12" r="3" />
      <path
        d="M19.4 15a1.7 1.7 0 0 0 .3 1.9l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.9-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1A1.7 1.7 0 0 0 8.9 19a1.7 1.7 0 0 0-1.9.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.9 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1A1.7 1.7 0 0 0 4.6 8.3a1.7 1.7 0 0 0-.3-1.9l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.9.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.9-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.9V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1Z"
      />
    </symbol>
  </svg>
</template>

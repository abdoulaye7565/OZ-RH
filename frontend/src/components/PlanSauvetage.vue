<script setup>
/**
 * Accès en un geste au plan de sauvetage et aux numéros d'urgence (prompt 2.3).
 *
 * Absent de la maquette de référence (aucun bouton ni écran dédié dans
 * Maquettes_SHEQ_Management_v2.html) : construit spécifiquement pour ce
 * prompt. Contenu repris — pas inventé — de
 * 03-Procedures_et_consignes/PLA-SHEQ-002_Plan_Sauvetage_Hauteur.docx
 * (numéros d'urgence maliens, conduite à tenir), condensé pour un écran de
 * téléphone. Codé en dur ici faute de module Documents (lot 4.3) capable de
 * le servir dynamiquement — à remplacer par un appel API quand ce module
 * existera.
 */
import Icone from "./Icone.vue";
</script>

<template>
  <details class="urgence">
    <summary><Icone nom="shield" taille="sm" />Plan de sauvetage &amp; urgence</summary>
    <div class="contenu">
      <div class="numero">
        <span>SAMU</span>
        <a href="tel:15">15</a>
      </div>
      <div class="numero">
        <span>Protection civile</span>
        <a href="tel:18">18</a>
      </div>
      <p>
        <b>En cas de chute ou de malaise :</b> le surveillant alerte immédiatement les secours
        en précisant le lieu exact, qu'il s'agit d'une personne suspendue en hauteur, son état
        et l'accès au site. Prévenir aussi la direction et le référent SHEQ. Ne jamais laisser
        la victime sans surveillance.
      </p>
      <p>
        <b>En attendant les secours :</b> parler à la victime en permanence pour la garder
        consciente. Si elle est suspendue et consciente, lui demander de bouger les jambes pour
        relancer la circulation. Une descente ne s'improvise jamais : seule une personne formée
        et en sécurité peut la réaliser.
      </p>
      <p style="margin-bottom: 0; color: var(--mut)">Réf. PLA-SHEQ-002 — plan complet sur le poste de gestion.</p>
    </div>
  </details>
</template>

<script setup>
/**
 * Cloche de notifications — bouton d'en-tête (mobile #s-home, desktop
 * .gestion-top), maquette v2 ligne 299 et Desktop ligne 244. Les deux
 * maquettes ne montrent que le bouton et son point rouge ("N non lues") :
 * aucune n'a de fragment pour le panneau déroulant lui-même (pas
 * d'id="p-notif"/"s-notif") — construit ici pour rester cohérent avec le
 * reste du système visuel (.card), seule façon de rendre la cloche
 * réellement utile plutôt que décorative.
 *
 * Les classes CSS `.ib .dot`/`.ib .d` sont scopées par ancêtre (`.hd`
 * mobile, `.gestion-top` desktop) : ce composant fonctionne sans prop dans
 * les deux contextes, la bonne variante s'applique automatiquement selon
 * l'endroit où il est monté.
 */
import { computed, onBeforeUnmount, onMounted, ref } from "vue";
import Icone from "./Icone.vue";
import api from "../services/api";

const ouvert = ref(false);
const nonLues = ref(0);
const notifications = ref([]);
const chargement = ref(false);
const erreur = ref(null);
const racine = ref(null);

async function chargerCompteur() {
  try {
    const { non_lues } = await api.requete("/api/v1/notifications/compteur");
    nonLues.value = non_lues;
  } catch {
    // Le compteur n'est qu'un indicateur d'en-tête : une panne réseau ici ne
    // doit pas faire échouer le reste de l'écran, seulement laisser le
    // dernier compteur connu (jamais afficher un chiffre inventé).
  }
}

async function basculer() {
  ouvert.value = !ouvert.value;
  if (ouvert.value) await chargerListe();
}

async function chargerListe() {
  chargement.value = true;
  erreur.value = null;
  try {
    notifications.value = await api.requete("/api/v1/notifications");
  } catch (e) {
    erreur.value = e?.message ?? "Impossible de charger les notifications";
  } finally {
    chargement.value = false;
  }
}

async function marquerLue(notif) {
  if (notif.lue) return;
  try {
    await api.requete(`/api/v1/notifications/${notif.id}/lue`, { methode: "POST" });
    notif.lue = true;
    await chargerCompteur();
  } catch {
    // Best-effort : l'utilisateur peut réessayer en rouvrant le panneau.
  }
}

async function toutMarquerLu() {
  try {
    await api.requete("/api/v1/notifications/toutes-lues", { methode: "POST" });
    for (const n of notifications.value) n.lue = true;
    nonLues.value = 0;
  } catch {
    // idem : pas de blocage de l'interface pour une action secondaire.
  }
}

function formaterDate(iso) {
  return new Date(iso).toLocaleString("fr-FR", { day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit" });
}

const aDesNonLues = computed(() => nonLues.value > 0);

function clicExterieur(e) {
  if (ouvert.value && racine.value && !racine.value.contains(e.target)) ouvert.value = false;
}

onMounted(() => {
  chargerCompteur();
  document.addEventListener("click", clicExterieur);
});
onBeforeUnmount(() => document.removeEventListener("click", clicExterieur));
</script>

<template>
  <div ref="racine" style="position: relative; display: inline-block">
    <button class="ib" aria-label="Notifications" @click.stop="basculer">
      <Icone nom="bell" />
      <span v-if="aDesNonLues" class="dot d"></span>
    </button>

    <div v-if="ouvert" class="notif-panel">
      <div class="ph">
        <span>Notifications</span>
        <span v-if="notifications.some((n) => !n.lue)" @click="toutMarquerLu">Tout marquer comme lu</span>
      </div>
      <div v-if="chargement" class="notif-empty">Chargement…</div>
      <div v-else-if="erreur" class="notif-empty">{{ erreur }}</div>
      <div v-else-if="!notifications.length" class="notif-empty">Aucune notification.</div>
      <template v-else>
        <div
          v-for="n in notifications"
          :key="n.id"
          class="notif-item"
          :class="{ 'non-lue': !n.lue }"
          role="button"
          tabindex="0"
          @click="marquerLue(n)"
          @keydown.enter="marquerLue(n)"
        >
          <div class="msg">{{ n.message }}</div>
          <div class="meta">{{ formaterDate(n.cree_le) }}</div>
        </div>
      </template>
    </div>
  </div>
</template>

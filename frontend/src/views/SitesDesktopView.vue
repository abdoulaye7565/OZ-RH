<script setup>
/**
 * Sites — vue desktop (pas de maquette dédiée : l'entité SITE est hors
 * dictionnaire, section 5.2.3 du CDC).
 *
 * Ajouté le 2026-09-10 (retour direct de l'utilisateur : « on a un seul site
 * alors que nous intervenons sur plusieurs sites ») : jusqu'ici les sites
 * n'étaient créés qu'en base, l'application ne faisait que les lister pour
 * résoudre un site_id en nom. Écran réservé à l'administrateur (comme
 * Utilisateurs & rôles — `Permissions.GERER_SITES`), aucun équivalent mobile.
 *
 * Un site ne se supprime pas : on l'archive (CLAUDE.md §2). Le serveur
 * refuse l'archivage tant qu'un équipement ou un permis en cours y est
 * rattaché — le message est remonté tel quel dans le bandeau.
 */
import { computed, onMounted, ref } from "vue";
import BarrePagination from "../components/BarrePagination.vue";
import Icone from "../components/Icone.vue";
import Modal from "../components/Modal.vue";
import ModalConfirmation from "../components/ModalConfirmation.vue";
import { useRechercheEtPagination } from "../composables/useRechercheEtPagination";
import { TYPES_SITE, useSitesStore } from "../stores/sites";

const sites = useSitesStore();
onMounted(() => sites.charger());

const parType = computed(() => ({
  siege: sites.liste.filter((s) => s.type === "siege").length,
  client: sites.liste.filter((s) => s.type === "client").length,
}));

function correspond(s, terme) {
  return (
    s.nom?.toLowerCase().includes(terme) ||
    s.adresse?.toLowerCase().includes(terme) ||
    sites.libelleType(s.type).toLowerCase().includes(terme)
  );
}
const { recherche, page, totalPages, resultats, elementsPage, allerPage } =
  useRechercheEtPagination(computed(() => sites.liste), correspond, 15);

const modaleOuverte = ref(false);
const enEdition = ref(null); // le site en cours de modification, ou null (création)
const form = ref({ nom: "", type: "client", adresse: "" });
const erreurForm = ref(null);
const enregistrement = ref(false);

function ouvrirCreation() {
  enEdition.value = null;
  form.value = { nom: "", type: "client", adresse: "" };
  erreurForm.value = null;
  modaleOuverte.value = true;
}
function ouvrirEdition(s) {
  enEdition.value = s;
  form.value = { nom: s.nom, type: s.type, adresse: s.adresse ?? "" };
  erreurForm.value = null;
  modaleOuverte.value = true;
}

async function soumettre() {
  erreurForm.value = null;
  enregistrement.value = true;
  try {
    const donnees = { nom: form.value.nom, type: form.value.type, adresse: form.value.adresse || null };
    if (enEdition.value) {
      await sites.modifier(enEdition.value.id, donnees);
    } else {
      await sites.creer(donnees);
    }
    modaleOuverte.value = false;
  } catch (e) {
    erreurForm.value = e?.message ?? "Impossible d'enregistrer ce site";
  } finally {
    enregistrement.value = false;
  }
}

const aArchiver = ref(null);
async function confirmerArchivage() {
  const s = aArchiver.value;
  aArchiver.value = null;
  try {
    await sites.archiver(s.id);
  } catch (e) {
    sites.erreur = e?.message ?? "Impossible d'archiver ce site";
  }
}
</script>

<template>
  <div>
    <div v-if="sites.erreur" class="banner err">{{ sites.erreur }}</div>

    <div class="filters">
      <span class="tag t-gy">{{ sites.liste.length }} site{{ sites.liste.length > 1 ? "s" : "" }}</span>
      <span class="tag t-bl">{{ parType.siege }} siège{{ parType.siege > 1 ? "s" : "" }}</span>
      <span class="tag t-gd">{{ parType.client }} site{{ parType.client > 1 ? "s" : "" }} client</span>
      <span style="flex: 1"></span>
      <div class="srch">
        <Icone nom="search" taille="sm" />
        <input v-model="recherche" placeholder="Rechercher un site, une adresse…" />
      </div>
      <button class="btn pri sm" style="width: auto" @click="ouvrirCreation">
        <Icone nom="plus" taille="sm" />Nouveau site
      </button>
    </div>

    <Modal v-if="modaleOuverte" :titre="enEdition ? 'Modifier le site' : 'Nouveau site'" @fermer="modaleOuverte = false">
      <label class="f">Nom</label>
      <input v-model="form.nom" class="inp" placeholder="Ex. Antenne Kayes" />
      <label class="f">Type</label>
      <select v-model="form.type" class="inp">
        <option v-for="t in TYPES_SITE" :key="t.valeur" :value="t.valeur">{{ t.libelle }}</option>
      </select>
      <label class="f">Adresse (facultatif)</label>
      <input v-model="form.adresse" class="inp" placeholder="Ville, quartier, repère" />

      <div v-if="erreurForm" class="banner err" style="margin: 8px 0">{{ erreurForm }}</div>
      <div style="display: flex; gap: 8px; margin-top: 10px">
        <button class="btn pri" style="width: auto" :disabled="enregistrement || !form.nom.trim()" @click="soumettre">
          {{ enEdition ? "Enregistrer" : "Créer le site" }}
        </button>
        <button class="btn gh" style="width: auto" @click="modaleOuverte = false">Annuler</button>
      </div>
    </Modal>

    <div class="card">
      <div class="ch"><Icone nom="door" /><h3>Sites d'intervention</h3></div>
      <table>
        <thead><tr><th>Nom</th><th>Type</th><th>Adresse</th><th></th></tr></thead>
        <tbody>
          <tr v-for="s in elementsPage" :key="s.id">
            <td><b>{{ s.nom }}</b></td>
            <td><span class="tag" :class="s.type === 'siege' ? 't-bl' : 't-gd'">{{ sites.libelleType(s.type) }}</span></td>
            <td>{{ s.adresse ?? "—" }}</td>
            <td style="text-align: right; white-space: nowrap">
              <button class="btn gh sm" style="width: auto" @click="ouvrirEdition(s)">Modifier</button>
              <button class="btn gh sm" style="width: auto; margin-left: 6px" @click="aArchiver = s">Archiver</button>
            </td>
          </tr>
          <tr v-if="!sites.chargement && !sites.liste.length">
            <td colspan="4" style="color: var(--mut)">Aucun site. Créez-en un pour commencer.</td>
          </tr>
          <tr v-if="sites.liste.length && !resultats.length"><td colspan="4" style="color: var(--mut)">Aucun site ne correspond à la recherche.</td></tr>
        </tbody>
      </table>
      <BarrePagination :page="page" :total-pages="totalPages" @changer="allerPage">
        Un site archivé reste rattaché à l'historique (inspections, permis…) mais n'est plus proposé à la saisie.
      </BarrePagination>
    </div>

    <ModalConfirmation
      v-if="aArchiver"
      titre="Archiver le site"
      :message="`Archiver « ${aArchiver.nom} » ? Il n'apparaîtra plus dans les listes de saisie (l'historique reste intact).`"
      libelle-confirmer="Archiver"
      @confirmer="confirmerArchivage"
      @annuler="aArchiver = null"
    />
  </div>
</template>

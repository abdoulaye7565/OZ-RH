<script setup>
/**
 * Visiteurs — vue desktop (maquette #p-visit).
 *
 * Formulaire "Nouveau visiteur" passé en fenêtre modale le 2026-09-09
 * (retour direct de l'utilisateur) : restait affiché en permanence
 * jusqu'ici, contrairement à la quasi-totalité des autres écrans desktop
 * (Actions, Risques, Parc, Utilisateurs...) où un formulaire de création
 * s'ouvre au clic et se referme après l'action — écart d'origine, pas un
 * choix délibéré documenté, corrigé ici.
 *
 * Registre + archivage ajoutés le 2026-09-09 (retour direct de
 * l'utilisateur — "on doit permettre d'archiver les visiteurs") : jusqu'ici
 * cet écran ne montrait que les présents, le registre complet
 * (`visiteurs.liste`, déjà chargé par charger() mais jamais affiché) et
 * l'archivage vivent ici sur desktop uniquement — écran de gestion/
 * historique, pas la saisie rapide terrain (mobile, VisiteursView.vue,
 * volontairement inchangé). Un visiteur encore présent ne peut pas être
 * archivé (le serveur le refuse de toute façon, 400 — voir
 * visiteur_service.archiver_visiteur) : seuls les partis apparaissent avec
 * un bouton "Archiver" dans le registre.
 */
import { computed, onMounted, ref } from "vue";
import BarrePagination from "../components/BarrePagination.vue";
import Icone from "../components/Icone.vue";
import Modal from "../components/Modal.vue";
import ModalConfirmation from "../components/ModalConfirmation.vue";
import { useRechercheEtPagination } from "../composables/useRechercheEtPagination";
import { useVisiteursStore } from "../stores/visiteurs";

const visiteurs = useVisiteursStore();
onMounted(() => visiteurs.charger());

const partis = computed(() => visiteurs.liste.filter((v) => v.heure_depart !== null));

function correspond(v, terme) {
  return (
    v.nom?.toLowerCase().includes(terme) ||
    v.societe?.toLowerCase().includes(terme) ||
    v.motif?.toLowerCase().includes(terme)
  );
}
const { recherche, page, totalPages, resultats, elementsPage, allerPage } =
  useRechercheEtPagination(partis, correspond, 15);

const aArchiver = ref(null);
async function confirmerArchivage() {
  const v = aArchiver.value;
  aArchiver.value = null;
  try {
    await visiteurs.archiver(v.id);
  } catch (e) {
    visiteurs.erreur = e?.message ?? "Impossible d'archiver ce visiteur";
  }
}

const formulaireOuvert = ref(false);
const vide = () => ({ nom: "", societe: "", motif: "", personne_visitee: "", consignes_lues: false });
const nouveau = ref(vide());
const erreur = ref(null);

function ouvrir() {
  formulaireOuvert.value = true;
  nouveau.value = vide();
  erreur.value = null;
}

async function soumettre() {
  erreur.value = null;
  try {
    await visiteurs.enregistrer(nouveau.value);
    formulaireOuvert.value = false;
  } catch (e) {
    erreur.value = e?.message ?? "Impossible d'enregistrer ce visiteur — les consignes doivent être cochées";
  }
}
function formaterHeure(iso) {
  return new Date(iso).toLocaleTimeString("fr-FR", { hour: "2-digit", minute: "2-digit" });
}
function formaterDateHeure(iso) {
  return new Date(iso).toLocaleString("fr-FR", { day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit" });
}
</script>

<template>
  <div>
    <div v-if="visiteurs.erreur" class="banner err">{{ visiteurs.erreur }}</div>

    <div class="filters">
      <span style="flex: 1"></span>
      <button class="btn pri sm" style="width: auto" @click="ouvrir">
        <Icone nom="plus" taille="sm" />Nouveau visiteur
      </button>
    </div>

    <Modal v-if="formulaireOuvert" titre="Nouveau visiteur" @fermer="formulaireOuvert = false">
      <label class="f">Nom et prénom</label><input v-model="nouveau.nom" class="inp" />
      <label class="f">Motif</label><input v-model="nouveau.motif" class="inp" />
      <label class="f">Société</label><input v-model="nouveau.societe" class="inp" />
      <label class="f">Personne visitée</label><input v-model="nouveau.personne_visitee" class="inp" />
      <label style="display: block; margin: 10px 0; font-size: 12.5px; font-weight: 650">
        <input v-model="nouveau.consignes_lues" type="checkbox" /> Consignes de sécurité lues et acceptées
      </label>
      <div v-if="erreur" class="banner err" style="margin-bottom: 8px">{{ erreur }}</div>
      <div style="display: flex; gap: 8px">
        <button class="btn gold" style="width: auto" @click="soumettre">Enregistrer l'arrivée</button>
        <button class="btn gh" style="width: auto" @click="formulaireOuvert = false">Annuler</button>
      </div>
    </Modal>

    <div class="card">
      <div class="ch"><Icone nom="shield" /><h3>Présents sur site</h3></div>
      <div class="cb">
        <div v-for="v in visiteurs.presents" :key="v.id" class="kv">
          <span>{{ v.nom }}{{ v.societe ? ` — ${v.societe}` : "" }} · {{ formaterHeure(v.heure_arrivee) }}</span>
          <button class="btn gh sm" style="width: auto" @click="visiteurs.enregistrerDepart(v.id)">Départ</button>
        </div>
        <p v-if="!visiteurs.presents.length" style="color: var(--mut); font-size: 12.5px">Aucun visiteur sur site.</p>
      </div>
    </div>

    <div class="card" style="margin-top: 14px">
      <div class="ch">
        <Icone nom="clock" /><h3>Registre — visiteurs partis</h3>
        <span style="flex: 1"></span>
        <div class="srch">
          <Icone nom="search" taille="sm" />
          <input v-model="recherche" placeholder="Rechercher un nom, une société…" />
        </div>
      </div>
      <table>
        <thead><tr><th>Nom</th><th>Motif</th><th>Arrivée</th><th>Départ</th><th></th></tr></thead>
        <tbody>
          <tr v-for="v in elementsPage" :key="v.id">
            <td><b>{{ v.nom }}</b>{{ v.societe ? ` — ${v.societe}` : "" }}</td>
            <td>{{ v.motif }}</td>
            <td>{{ formaterDateHeure(v.heure_arrivee) }}</td>
            <td>{{ formaterDateHeure(v.heure_depart) }}</td>
            <td><button class="btn gh sm" style="width: auto" @click="aArchiver = v">Archiver</button></td>
          </tr>
          <tr v-if="!partis.length"><td colspan="5" style="color: var(--mut)">Aucun visiteur parti à archiver.</td></tr>
          <tr v-if="partis.length && !resultats.length"><td colspan="5" style="color: var(--mut)">Aucun visiteur ne correspond à la recherche.</td></tr>
        </tbody>
      </table>
      <BarrePagination :page="page" :total-pages="totalPages" @changer="allerPage">
        {{ resultats.length }} visiteur{{ resultats.length > 1 ? "s" : "" }} dans le registre
      </BarrePagination>
    </div>

    <ModalConfirmation
      v-if="aArchiver"
      titre="Archiver le visiteur"
      :message="`Archiver « ${aArchiver.nom} » du registre ? La visite reste dans l'historique mais n'apparaît plus ici.`"
      libelle-confirmer="Archiver"
      @confirmer="confirmerArchivage"
      @annuler="aArchiver = null"
    />
  </div>
</template>

<script setup>
/**
 * Formations — vue desktop (maquette #p-form). Écart : le passage de quiz
 * n'est proposé que côté mobile (FormationsView.vue) — une action
 * individuelle, pas une vue de pilotage.
 *
 * Émargement + clôture de séance ajoutés le 2026-09-19 (revue de
 * compatibilité front/back, "tu corriges tout") : POST .../emargement et
 * POST .../cloturer existaient côté serveur depuis le prompt 4.2, jamais
 * câblés à un écran — une séance restait éternellement "planifiée". Réservé
 * à GERER_FORMATIONS (referent_sheq/administrateur) : même garde locale que
 * pour "Nouvelle séance", qui n'était elle-même pas gardée jusqu'ici (aucune
 * clé de permission sur le lien de la barre latérale, donc un rôle sans ce
 * droit qui atteint cet écran voyait un bouton qui échouerait en 403).
 */
import { computed, onMounted, ref } from "vue";
import BarrePagination from "../components/BarrePagination.vue";
import Icone from "../components/Icone.vue";
import Modal from "../components/Modal.vue";
import ModalConfirmation from "../components/ModalConfirmation.vue";
import { useRechercheEtPagination } from "../composables/useRechercheEtPagination";
import api from "../services/api";
import { useAuthStore } from "../stores/auth";
import { useFormationsStore } from "../stores/formations";
import { formaterDateCivile } from "../utils/dates";

const auth = useAuthStore();
const formations = useFormationsStore();
const matrice = ref([]);

const peutGerer = computed(() => ["referent_sheq", "administrateur"].includes(auth.utilisateur?.role));

function correspond(l, terme) {
  return (
    nomUtilisateur(l.utilisateur_id).toLowerCase().includes(terme) ||
    (l.libelle_competence ?? "").toLowerCase().includes(terme)
  );
}
const { recherche, page, totalPages, resultats, elementsPage, allerPage } =
  useRechercheEtPagination(matrice, correspond, 15);

onMounted(async () => {
  await formations.charger();
  try {
    matrice.value = await api.requete("/api/v1/formations/matrice");
  } catch {
    // Réservé à un rôle de vue d'ensemble (référent SHEQ/responsable/admin) —
    // un rôle sans ce droit voit simplement une matrice vide plutôt qu'une erreur bloquante.
  }
});

function nomUtilisateur(id) {
  return formations.nomUtilisateur(id) ?? `Utilisateur #${id}`;
}

const formulaireOuvert = ref(false);
const nouvelle = ref({ theme: "", date: "", lieu: "", animateur_id: "", competence_id: "" });
const erreurFormulaire = ref(null);

// POST /formations/competences existait côté serveur (testé) sans aucune UI
// pour l'atteindre — le référentiel de compétences ne pouvait donc jamais
// être alimenté (2026-09-19, même campagne).
const formulaireCompetenceOuvert = ref(false);
const nouvelleCompetence = ref({ libelle: "", periodicite_mois: 12 });
const erreurCompetence = ref(null);
async function soumettreCompetence() {
  erreurCompetence.value = null;
  try {
    await formations.creerCompetence({
      libelle: nouvelleCompetence.value.libelle,
      periodicite_mois: Number(nouvelleCompetence.value.periodicite_mois),
    });
    formulaireCompetenceOuvert.value = false;
    nouvelleCompetence.value = { libelle: "", periodicite_mois: 12 };
  } catch (e) {
    erreurCompetence.value = e?.message ?? "Impossible d'enregistrer cette compétence";
  }
}

async function soumettre() {
  erreurFormulaire.value = null;
  try {
    await formations.creerSeance({
      theme: nouvelle.value.theme, date: nouvelle.value.date, lieu: nouvelle.value.lieu,
      animateur_id: Number(nouvelle.value.animateur_id),
      competence_id: nouvelle.value.competence_id ? Number(nouvelle.value.competence_id) : null,
    });
    formulaireOuvert.value = false;
    nouvelle.value = { theme: "", date: "", lieu: "", animateur_id: "", competence_id: "" };
  } catch (e) {
    erreurFormulaire.value = e?.message ?? "Impossible d'enregistrer cette séance";
  }
}

// --- Correction d'une séance encore planifiée (2026-09-10). Refusé serveur
// une fois réalisée (409). ---
const edition = ref(null);
const champsEdition = ref({ theme: "", date: "", lieu: "", animateur_id: "" });
const erreurEdition = ref(null);

function ouvrirEdition(s) {
  edition.value = s;
  champsEdition.value = { theme: s.theme, date: s.date, lieu: s.lieu, animateur_id: s.animateur_id };
  erreurEdition.value = null;
}
async function soumettreEdition() {
  erreurEdition.value = null;
  try {
    await formations.modifierSeance(edition.value.id, {
      ...champsEdition.value, animateur_id: Number(champsEdition.value.animateur_id),
    });
    edition.value = null;
  } catch (e) {
    erreurEdition.value = e?.message ?? "Impossible d'enregistrer la correction";
  }
}

// --- Émargement (2026-09-19) ---
const seanceEmargement = ref(null);
const presences = ref({}); // utilisateur_id -> bool
const chargementPresences = ref(false);
const erreurEmargement = ref(null);

async function ouvrirEmargement(s) {
  seanceEmargement.value = s;
  presences.value = {};
  erreurEmargement.value = null;
  chargementPresences.value = true;
  try {
    const existants = await formations.listerEmargements(s.id);
    for (const e of existants) presences.value[e.participant_id] = e.present;
  } catch (e) {
    erreurEmargement.value = e?.message ?? "Impossible de charger les présences déjà enregistrées";
  } finally {
    chargementPresences.value = false;
  }
}

async function basculerPresence(utilisateurId) {
  const nouvellePresence = !presences.value[utilisateurId];
  try {
    await formations.emarger(seanceEmargement.value.id, utilisateurId, nouvellePresence);
    presences.value[utilisateurId] = nouvellePresence;
  } catch (e) {
    erreurEmargement.value = e?.message ?? "Impossible d'enregistrer cette présence";
  }
}

// --- Clôture de séance (2026-09-19) ---
const aCloturer = ref(null);
const messageCloture = computed(() => {
  if (!aCloturer.value) return "";
  const suite = aCloturer.value.competence_id
    ? "Chaque participant marqué présent verra son habilitation renouvelée."
    : "Cette séance n'est liée à aucune compétence : aucune habilitation ne sera renouvelée.";
  return `Clôturer « ${aCloturer.value.theme} » ? ${suite} Action irréversible.`;
});
async function confirmerCloture() {
  const s = aCloturer.value;
  aCloturer.value = null;
  try {
    await formations.cloturerSeance(s.id);
  } catch (e) {
    formations.erreur = e?.message ?? "Impossible de clôturer cette séance";
  }
}
</script>

<template>
  <div>
    <div v-if="formations.erreur" class="banner err">{{ formations.erreur }}</div>

    <Modal v-if="formulaireOuvert" titre="Nouvelle séance" @fermer="formulaireOuvert = false">
      <label class="f">Thème</label><input v-model="nouvelle.theme" class="inp" />
      <label class="f">Date</label><input v-model="nouvelle.date" type="date" class="inp" />
      <label class="f">Lieu</label><input v-model="nouvelle.lieu" class="inp" />
      <label class="f">Animateur</label>
      <select v-model="nouvelle.animateur_id" class="inp">
        <option value="" disabled>Choisir…</option>
        <option v-for="u in formations.utilisateurs" :key="u.id" :value="u.id">{{ u.prenom }} {{ u.nom }}</option>
      </select>
      <label class="f">Compétence liée (facultatif)</label>
      <select v-model="nouvelle.competence_id" class="inp">
        <option value="">Aucune — pas de renouvellement d'habilitation à la clôture</option>
        <option v-for="c in formations.competences" :key="c.id" :value="c.id">{{ c.libelle }}</option>
      </select>
      <div v-if="erreurFormulaire" class="banner err" style="margin-top: 8px">{{ erreurFormulaire }}</div>
      <div style="display: flex; gap: 8px; margin-top: 8px">
        <button class="btn pri" style="width: auto" @click="soumettre">Enregistrer</button>
        <button class="btn gh" style="width: auto" @click="formulaireOuvert = false">Annuler</button>
      </div>
    </Modal>

    <div class="grid2" style="grid-template-columns: 1fr 1fr">
      <div class="card">
        <div class="ch">
          <Icone nom="cap" /><h3>Séances</h3>
          <span v-if="peutGerer" class="r" role="button" tabindex="0" @click="formulaireOuvert = true" @keydown.enter="formulaireOuvert = true">Nouvelle séance</span>
        </div>
        <div class="cb">
          <div v-for="s in formations.seances" :key="s.id" class="kv" style="flex-wrap: wrap">
            <span>{{ s.theme }} — {{ formaterDateCivile(s.date) }}</span>
            <span style="display: flex; align-items: center; gap: 8px">
              <b>{{ s.statut === "planifiee" ? "Planifiée" : "Réalisée" }}</b>
              <template v-if="s.statut === 'planifiee' && peutGerer">
                <button class="btn gh sm" style="width: auto" @click="ouvrirEdition(s)">Modifier</button>
                <button class="btn gh sm" style="width: auto" @click="ouvrirEmargement(s)">Émarger</button>
                <button class="btn gh sm" style="width: auto" @click="aCloturer = s">Clôturer</button>
              </template>
            </span>
          </div>
          <p v-if="!formations.seances.length" style="color: var(--mut); font-size: 12.5px">Aucune séance planifiée.</p>
        </div>
      </div>
      <div class="card">
        <div class="ch">
          <Icone nom="check" /><h3>Compétences</h3>
          <span v-if="peutGerer" class="r" role="button" tabindex="0" @click="formulaireCompetenceOuvert = true" @keydown.enter="formulaireCompetenceOuvert = true">Nouvelle compétence</span>
        </div>
        <div class="cb">
          <div v-for="c in formations.competences" :key="c.id" class="kv">
            <span>{{ c.libelle }}</span><b>Recyclage {{ c.periodicite_mois }} mois</b>
          </div>
          <p v-if="!formations.competences.length" style="color: var(--mut); font-size: 12.5px">Aucune compétence enregistrée.</p>
        </div>
      </div>
    </div>

    <div class="card">
      <div class="ch">
        <h3>Matrice de compétences</h3>
        <span style="flex: 1"></span>
        <div class="srch">
          <Icone nom="search" taille="sm" />
          <input v-model="recherche" placeholder="Rechercher un collaborateur, une compétence…" />
        </div>
      </div>
      <table>
        <thead><tr><th>Collaborateur</th><th>Compétence</th><th>Obtenue le</th><th>Expire le</th><th>Statut</th></tr></thead>
        <tbody>
          <tr v-for="(l, i) in elementsPage" :key="i">
            <td><b>{{ nomUtilisateur(l.utilisateur_id) }}</b></td>
            <td>{{ l.libelle_competence }}</td>
            <td>{{ formaterDateCivile(l.date_obtention) }}</td>
            <td>{{ formaterDateCivile(l.date_expiration) }}</td>
            <td><span class="tag" :class="l.expiree ? 't-or' : 't-gr'">{{ l.expiree ? "À renouveler" : "Valide" }}</span></td>
          </tr>
          <tr v-if="!matrice.length"><td colspan="5" style="color: var(--mut)">Aucune habilitation enregistrée.</td></tr>
          <tr v-if="matrice.length && !resultats.length"><td colspan="5" style="color: var(--mut)">Aucune habilitation ne correspond à la recherche.</td></tr>
        </tbody>
      </table>
      <BarrePagination :page="page" :total-pages="totalPages" @changer="allerPage">
        {{ resultats.length }} sur {{ matrice.length }} habilitation{{ matrice.length > 1 ? "s" : "" }}
      </BarrePagination>
    </div>

    <Modal v-if="edition" titre="Corriger la séance" @fermer="edition = null">
      <label class="f">Thème</label><input v-model="champsEdition.theme" class="inp" />
      <label class="f">Date</label><input v-model="champsEdition.date" type="date" class="inp" />
      <label class="f">Lieu</label><input v-model="champsEdition.lieu" class="inp" />
      <label class="f">Animateur</label>
      <select v-model="champsEdition.animateur_id" class="inp">
        <option v-for="u in formations.utilisateurs" :key="u.id" :value="u.id">{{ u.prenom }} {{ u.nom }}</option>
      </select>
      <div v-if="erreurEdition" class="banner err" style="margin: 8px 0">{{ erreurEdition }}</div>
      <div style="display: flex; gap: 8px; margin-top: 10px">
        <button class="btn pri" style="width: auto" @click="soumettreEdition">Enregistrer</button>
        <button class="btn gh" style="width: auto" @click="edition = null">Annuler</button>
      </div>
    </Modal>

    <Modal v-if="seanceEmargement" :titre="`Émargement — ${seanceEmargement.theme}`" @fermer="seanceEmargement = null">
      <div v-if="chargementPresences" class="skel" style="height: 100px"></div>
      <template v-else>
        <p style="font-size: 12.5px; color: var(--mut); margin-bottom: 8px">
          Cochez les participants présents à cette séance. Chaque clic enregistre immédiatement la présence.
        </p>
        <div v-if="erreurEmargement" class="banner err" style="margin-bottom: 8px">{{ erreurEmargement }}</div>
        <div style="max-height: 340px; overflow-y: auto">
          <label v-for="u in formations.utilisateurs" :key="u.id" class="kv" style="cursor: pointer">
            <span>{{ u.prenom }} {{ u.nom }}</span>
            <input
              type="checkbox"
              :checked="!!presences[u.id]"
              @change="basculerPresence(u.id)"
            />
          </label>
        </div>
      </template>
      <div style="display: flex; gap: 8px; margin-top: 10px">
        <button class="btn pri" style="width: auto" @click="seanceEmargement = null">Terminer</button>
      </div>
    </Modal>

    <Modal v-if="formulaireCompetenceOuvert" titre="Nouvelle compétence" @fermer="formulaireCompetenceOuvert = false">
      <label class="f">Libellé</label><input v-model="nouvelleCompetence.libelle" class="inp" placeholder="Travail en hauteur, port du harnais…" />
      <label class="f">Périodicité de recyclage (mois)</label><input v-model="nouvelleCompetence.periodicite_mois" type="number" min="1" class="inp" />
      <div v-if="erreurCompetence" class="banner err" style="margin-top: 8px">{{ erreurCompetence }}</div>
      <div style="display: flex; gap: 8px; margin-top: 8px">
        <button class="btn pri" style="width: auto" @click="soumettreCompetence">Enregistrer</button>
        <button class="btn gh" style="width: auto" @click="formulaireCompetenceOuvert = false">Annuler</button>
      </div>
    </Modal>

    <ModalConfirmation
      v-if="aCloturer"
      titre="Clôturer cette séance"
      :message="messageCloture"
      libelle-confirmer="Clôturer"
      @confirmer="confirmerCloture"
      @annuler="aCloturer = null"
    />
  </div>
</template>

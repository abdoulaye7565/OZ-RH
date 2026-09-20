<script setup>
/**
 * Plan d'action — vue desktop (maquette #p-act). Écart : "Origine" affiche
 * simplement "Risque" (pas de résolution du numéro de risque depuis
 * risque_id sans appel supplémentaire par ligne) ; pas de pagination.
 *
 * Suivi d'une action ajouté le 2026-09-10 (retour direct de l'utilisateur —
 * "on ne peut pas modifier le statut de l'action") : jusqu'ici la colonne
 * "Statut" était en lecture seule côté desktop alors que le back-end
 * (PATCH /actions/{id}/avancement et /statut) et le store
 * (mettreAJourAvancement, changerStatut) exposaient déjà tout. Le suivi se
 * fait via une fenêtre modale par ligne : avancement (%), indicateur de
 * réalisation (obligatoire pour clôturer — règle serveur
 * action_service.changer_statut), puis "Démarrer" (ouverte -> en cours) ou
 * "Clôturer" (-> clôturée, aucun retour en arrière). Les refus serveur
 * (transition invalide, clôture sans indicateur, accès refusé) sont
 * remontés dans la modale.
 */
import { computed, onMounted, ref } from "vue";
import BarrePagination from "../components/BarrePagination.vue";
import Icone from "../components/Icone.vue";
import Modal from "../components/Modal.vue";
import { useRechercheEtPagination } from "../composables/useRechercheEtPagination";
import { useActionsStore } from "../stores/actions";
import { formaterDateCivile } from "../utils/dates";

const actions = useActionsStore();
onMounted(() => actions.charger());

const filtre = ref("toutes");
const listeFiltree = computed(() => {
  if (filtre.value === "retard") return actions.liste.filter((a) => a.en_retard);
  if (filtre.value === "cours") return actions.liste.filter((a) => a.statut === "en_cours" && !a.en_retard);
  if (filtre.value === "realisees") return actions.liste.filter((a) => a.statut === "cloturee");
  return actions.liste;
});
const nombreEnRetard = computed(() => actions.liste.filter((a) => a.en_retard).length);
const nombreEnCours = computed(() => actions.liste.filter((a) => a.statut === "en_cours" && !a.en_retard).length);
const nombreRealisees = computed(() => actions.liste.filter((a) => a.statut === "cloturee").length);

function correspond(a, terme) {
  return (
    a.libelle?.toLowerCase().includes(terme) ||
    origine(a).toLowerCase().includes(terme) ||
    (actions.nomUtilisateur(a.responsable_id) ?? "").toLowerCase().includes(terme)
  );
}
const { recherche, page, totalPages, resultats, elementsPage, allerPage } =
  useRechercheEtPagination(listeFiltree, correspond, 10);

function etat(a) {
  if (a.statut === "cloturee") return { tag: "t-gr", libelle: "Réalisée", barre: "g" };
  if (a.en_retard) return { tag: "t-red", libelle: "En retard", barre: "o" };
  return { tag: "t-gd", libelle: "En cours", barre: "gd" };
}
function origine(a) {
  if (a.risque_id) return `Risque #${a.risque_id}`;
  if (a.signalement_id) return `Signalement #${a.signalement_id}`;
  if (a.inspection_id) return `Inspection #${a.inspection_id}`;
  if (a.cotation_audit_id) return "Écart d'audit";
  if (a.reponse_satisfaction_id) return "Satisfaction";
  return "—";
}
const formaterDate = formaterDateCivile;

// --- Suivi d'une action (avancement + statut) ---
const suivi = ref(null); // l'action en cours de suivi, ou null
const suiviAvancement = ref(0);
const suiviIndicateur = ref("");
const erreurSuivi = ref(null);
const enregistrementSuivi = ref(false);

function ouvrirSuivi(a) {
  suivi.value = a;
  suiviAvancement.value = a.avancement;
  suiviIndicateur.value = a.indicateur ?? "";
  erreurSuivi.value = null;
}
function fermerSuivi() {
  suivi.value = null;
}

async function enregistrerAvancement() {
  erreurSuivi.value = null;
  enregistrementSuivi.value = true;
  try {
    await actions.mettreAJourAvancement(suivi.value.id, Number(suiviAvancement.value), suiviIndicateur.value);
    fermerSuivi();
  } catch (e) {
    erreurSuivi.value = e?.message ?? "Impossible d'enregistrer l'avancement";
  } finally {
    enregistrementSuivi.value = false;
  }
}

async function changerStatut(nouveauStatut) {
  erreurSuivi.value = null;
  enregistrementSuivi.value = true;
  try {
    // Clôture : l'indicateur de réalisation est obligatoire (le serveur le
    // revérifie, 409). On enregistre d'abord avancement + indicateur s'ils
    // ont changé, puis on bascule le statut.
    if (nouveauStatut === "cloturee") {
      if (!suiviIndicateur.value.trim()) {
        erreurSuivi.value = "Renseigne l'indicateur de réalisation avant de clôturer.";
        return;
      }
      await actions.mettreAJourAvancement(suivi.value.id, Number(suiviAvancement.value), suiviIndicateur.value);
    }
    await actions.changerStatut(suivi.value.id, nouveauStatut);
    fermerSuivi();
  } catch (e) {
    erreurSuivi.value = e?.message ?? "Impossible de changer le statut";
  } finally {
    enregistrementSuivi.value = false;
  }
}

// --- Correction d'une action (libellé, responsable, échéance, type) — 2026-09-10.
// Refusé serveur sur une action clôturée. ---
const edition = ref(null);
const champsEdition = ref({ libelle: "", type_mesure: "corrective", responsable_id: "", echeance: "" });
const erreurEdition = ref(null);

function ouvrirEdition(a) {
  edition.value = a;
  champsEdition.value = {
    libelle: a.libelle, type_mesure: a.type_mesure,
    responsable_id: a.responsable_id, echeance: a.echeance,
  };
  erreurEdition.value = null;
}
async function soumettreEdition() {
  erreurEdition.value = null;
  try {
    await actions.modifier(edition.value.id, {
      libelle: champsEdition.value.libelle,
      type_mesure: champsEdition.value.type_mesure,
      responsable_id: Number(champsEdition.value.responsable_id),
      echeance: champsEdition.value.echeance,
    });
    edition.value = null;
  } catch (e) {
    erreurEdition.value = e?.message ?? "Impossible d'enregistrer la correction";
  }
}

const formulaireOuvert = ref(false);
const nouvelle = ref({ libelle: "", risque_id: "", type_mesure: "corrective", responsable_id: "", echeance: "" });
const erreurFormulaire = ref(null);

async function soumettre() {
  erreurFormulaire.value = null;
  try {
    await actions.creer({
      libelle: nouvelle.value.libelle, risque_id: Number(nouvelle.value.risque_id),
      type_mesure: nouvelle.value.type_mesure, responsable_id: Number(nouvelle.value.responsable_id),
      echeance: nouvelle.value.echeance,
    });
    formulaireOuvert.value = false;
    nouvelle.value = { libelle: "", risque_id: "", type_mesure: "corrective", responsable_id: "", echeance: "" };
  } catch (e) {
    erreurFormulaire.value = e?.message ?? "Impossible d'enregistrer cette action";
  }
}
</script>

<template>
  <div>
    <div v-if="actions.erreur" class="banner err">{{ actions.erreur }}</div>

    <div class="filters">
      <button class="seg" :class="{ on: filtre === 'toutes' }" @click="filtre = 'toutes'">Toutes · {{ actions.liste.length }}</button>
      <button class="seg" :class="{ on: filtre === 'retard' }" @click="filtre = 'retard'">En retard · {{ nombreEnRetard }}</button>
      <button class="seg" :class="{ on: filtre === 'cours' }" @click="filtre = 'cours'">En cours · {{ nombreEnCours }}</button>
      <button class="seg" :class="{ on: filtre === 'realisees' }" @click="filtre = 'realisees'">Réalisées · {{ nombreRealisees }}</button>
      <span style="flex: 1"></span>
      <div class="srch">
        <Icone nom="search" taille="sm" />
        <input v-model="recherche" placeholder="Rechercher une action, un responsable…" />
      </div>
      <button class="btn pri sm" style="width: auto" @click="formulaireOuvert = true"><Icone nom="plus" taille="sm" />Nouvelle action</button>
    </div>

    <Modal v-if="formulaireOuvert" titre="Nouvelle action (à partir d'un risque)" @fermer="formulaireOuvert = false">
      <div class="grid2">
        <div>
          <label class="f">Libellé</label>
          <input v-model="nouvelle.libelle" class="inp" />
          <label class="f">Risque d'origine</label>
          <select v-model="nouvelle.risque_id" class="inp">
            <option value="" disabled>Choisir…</option>
            <option v-for="r in actions.risques" :key="r.id" :value="r.id">{{ r.danger }}</option>
          </select>
        </div>
        <div>
          <label class="f">Type de mesure</label>
          <select v-model="nouvelle.type_mesure" class="inp">
            <option value="corrective">Corrective</option><option value="preventive">Préventive</option><option value="amelioration">Amélioration</option>
          </select>
          <label class="f">Responsable</label>
          <select v-model="nouvelle.responsable_id" class="inp">
            <option value="" disabled>Choisir…</option>
            <option v-for="u in actions.utilisateurs" :key="u.id" :value="u.id">{{ u.prenom }} {{ u.nom }}</option>
          </select>
          <label class="f">Échéance</label>
          <input v-model="nouvelle.echeance" type="date" class="inp" />
        </div>
      </div>
      <div v-if="erreurFormulaire" class="banner err" style="margin-top: 8px">{{ erreurFormulaire }}</div>
      <div style="display: flex; gap: 8px; margin-top: 10px">
        <button class="btn pri" style="width: auto" @click="soumettre">Enregistrer</button>
        <button class="btn gh" style="width: auto" @click="formulaireOuvert = false">Annuler</button>
      </div>
    </Modal>

    <Modal v-if="suivi" :titre="`Suivi — ${suivi.libelle}`" @fermer="fermerSuivi">
      <div class="kv"><span>Statut actuel</span><span class="tag" :class="etat(suivi).tag">{{ etat(suivi).libelle }}</span></div>
      <div class="kv"><span>Responsable</span><span>{{ actions.nomUtilisateur(suivi.responsable_id) ?? `Utilisateur #${suivi.responsable_id}` }}</span></div>
      <div class="kv"><span>Échéance</span><span>{{ formaterDate(suivi.echeance) }}</span></div>

      <template v-if="suivi.statut !== 'cloturee'">
        <label class="f">Avancement (%)</label>
        <input v-model="suiviAvancement" type="number" min="0" max="100" class="inp" />
        <label class="f">Indicateur de réalisation <span style="color: var(--mut)">(obligatoire pour clôturer)</span></label>
        <textarea v-model="suiviIndicateur" class="inp" rows="2" placeholder="Preuve / résultat mesurable de la mise en œuvre"></textarea>

        <div v-if="erreurSuivi" class="banner err" style="margin: 8px 0">{{ erreurSuivi }}</div>

        <div style="display: flex; flex-wrap: wrap; gap: 8px; margin-top: 10px">
          <button class="btn pri" style="width: auto" :disabled="enregistrementSuivi" @click="enregistrerAvancement">
            Enregistrer l'avancement
          </button>
          <button v-if="suivi.statut === 'ouverte'" class="btn gh" style="width: auto" :disabled="enregistrementSuivi" @click="changerStatut('en_cours')">
            Démarrer
          </button>
          <button class="btn gold" style="width: auto" :disabled="enregistrementSuivi" @click="changerStatut('cloturee')">
            Clôturer
          </button>
          <button class="btn gh" style="width: auto" @click="fermerSuivi">Annuler</button>
        </div>
      </template>
      <template v-else>
        <div class="kv"><span>Avancement</span><span>{{ suivi.avancement }} %</span></div>
        <div class="kv"><span>Indicateur</span><span>{{ suivi.indicateur ?? "—" }}</span></div>
        <p style="color: var(--mut); font-size: 12px; margin-top: 8px">Action clôturée — aucune modification possible (aucun retour en arrière).</p>
        <div style="margin-top: 10px"><button class="btn gh" style="width: auto" @click="fermerSuivi">Fermer</button></div>
      </template>
    </Modal>

    <Modal v-if="edition" titre="Corriger l'action" @fermer="edition = null">
      <label class="f">Libellé</label>
      <input v-model="champsEdition.libelle" class="inp" />
      <label class="f">Type de mesure</label>
      <select v-model="champsEdition.type_mesure" class="inp">
        <option value="corrective">Corrective</option><option value="preventive">Préventive</option><option value="amelioration">Amélioration</option>
      </select>
      <label class="f">Responsable</label>
      <select v-model="champsEdition.responsable_id" class="inp">
        <option v-for="u in actions.utilisateurs" :key="u.id" :value="u.id">{{ u.prenom }} {{ u.nom }}</option>
      </select>
      <label class="f">Échéance</label>
      <input v-model="champsEdition.echeance" type="date" class="inp" />
      <div v-if="erreurEdition" class="banner err" style="margin: 8px 0">{{ erreurEdition }}</div>
      <div style="display: flex; gap: 8px; margin-top: 10px">
        <button class="btn pri" style="width: auto" @click="soumettreEdition">Enregistrer</button>
        <button class="btn gh" style="width: auto" @click="edition = null">Annuler</button>
      </div>
    </Modal>

    <div class="card">
      <table>
        <thead><tr><th>Action</th><th>Origine</th><th>Responsable</th><th>Échéance</th><th style="width: 130px">Avancement</th><th>Statut</th><th></th></tr></thead>
        <tbody>
          <tr v-for="a in elementsPage" :key="a.id">
            <td><b>{{ a.libelle }}</b></td>
            <td><span class="tag t-gy">{{ origine(a) }}</span></td>
            <td>{{ actions.nomUtilisateur(a.responsable_id) ?? `Utilisateur #${a.responsable_id}` }}</td>
            <td>
              <b :style="a.en_retard ? 'color:var(--red)' : ''">{{ formaterDate(a.echeance) }}</b>
              <div class="sub" v-if="a.en_retard" style="color: var(--red)">En retard</div>
            </td>
            <td><div class="trk"><div class="fl" :class="etat(a).barre" :style="{ width: a.avancement + '%' }"></div></div><div class="sub">{{ a.avancement }} %</div></td>
            <td><span class="tag" :class="etat(a).tag">{{ etat(a).libelle }}</span></td>
            <td style="white-space: nowrap; text-align: right">
              <button v-if="a.statut !== 'cloturee'" class="btn gh sm" style="width: auto" @click="ouvrirEdition(a)">Modifier</button>
              <button class="btn gh sm" style="width: auto; margin-left: 6px" @click="ouvrirSuivi(a)">
                {{ a.statut === 'cloturee' ? 'Voir' : 'Suivi' }}
              </button>
            </td>
          </tr>
          <tr v-if="!actions.chargement && !listeFiltree.length"><td colspan="7" style="color: var(--mut)">Aucune action.</td></tr>
          <tr v-if="listeFiltree.length && !resultats.length"><td colspan="7" style="color: var(--mut)">Aucune action ne correspond à la recherche.</td></tr>
        </tbody>
      </table>
      <BarrePagination :page="page" :total-pages="totalPages" @changer="allerPage">
        {{ resultats.length }} action{{ resultats.length > 1 ? "s" : "" }} affichée{{ resultats.length > 1 ? "s" : "" }}
      </BarrePagination>
    </div>
  </div>
</template>

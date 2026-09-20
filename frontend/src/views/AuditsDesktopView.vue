<script setup>
/**
 * Audits internes & revues de direction — vue desktop (maquette #p-audit /
 * #p-revue, regroupées comme dans la barre latérale).
 *
 * Historique des revues, commentaire IA et solde des décisions ajoutés le
 * 2026-09-19 (revue de compatibilité front/back, "tu corriges tout") :
 * GET /revues (nouvelle route, aucune n'existait pour lister les revues déjà
 * créées), POST .../commentaire/generer, PATCH .../commentaire, POST
 * .../commentaire/valider et POST /revues/decisions/{id}/solder existaient
 * tous côté serveur (prompt 6.4 et 4.2) sans aucune UI — une revue restait
 * invisible après sa création, son commentaire de synthèse ne pouvait
 * jamais être pré-rédigé, et une décision ne pouvait jamais être marquée
 * traitée.
 */
import { computed, onMounted, ref } from "vue";
import { telechargerPdf } from "../utils/telechargement";
import Icone from "../components/Icone.vue";
import Modal from "../components/Modal.vue";
import { useAuditsStore } from "../stores/audits";
import { useAuthStore } from "../stores/auth";
import { formaterDateCivile } from "../utils/dates";

const auth = useAuthStore();
const audits = useAuditsStore();
onMounted(() => audits.charger());

// Le bouton "Nouvelle revue" n'avait jusqu'ici aucune garde locale (même
// classe de bug que EPI/Formations/Parc ce même jour) : un rôle sans
// GERER_REVUES (referent_sheq/responsable/administrateur) le voyait et
// essuyait un 403 à la création.
const peutGererRevues = computed(() => ["referent_sheq", "responsable", "administrateur"].includes(auth.utilisateur?.role));

const exigencesParChapitre = computed(() => {
  const groupes = {};
  for (const e of audits.exigences) {
    groupes[e.chapitre] ??= [];
    groupes[e.chapitre].push(e);
  }
  return groupes;
});
function cotationDe(exigenceId) {
  return audits.campagne?.cotations?.find((c) => c.exigence_id === exigenceId)?.cotation ?? null;
}

const pdfEnCours = ref(false);
async function telechargerRapportCampagne() {
  pdfEnCours.value = true;
  try {
    await telechargerPdf(
      `/api/v1/audits/campagnes/${audits.campagne.id}/export-pdf`,
      `${audits.campagne.reference ?? "campagne-audit-" + audits.campagne.id}.pdf`,
    );
  } catch (e) {
    audits.erreur = e?.message ?? "Téléchargement du rapport impossible";
  } finally {
    pdfEnCours.value = false;
  }
}

const revueOuverte = ref(false);
const nouvelleRevue = ref({ date: "", lieu: "", periode_debut: "", periode_fin: "", participants: "" });
const revueCreee = ref(null);
const erreurRevue = ref(null);

async function soumettreRevue() {
  erreurRevue.value = null;
  try {
    revueCreee.value = await audits.creerRevue(nouvelleRevue.value);
  } catch (e) {
    erreurRevue.value = e?.message ?? "Impossible d'enregistrer la revue";
  }
}
const nouvelleDecision = ref({ libelle: "", responsable_id: "", echeance: "" });
async function ajouterDecision() {
  await audits.ajouterDecision(revueCreee.value.id, {
    libelle: nouvelleDecision.value.libelle, responsable_id: Number(nouvelleDecision.value.responsable_id), echeance: nouvelleDecision.value.echeance,
  });
  nouvelleDecision.value = { libelle: "", responsable_id: "", echeance: "" };
}

// La revue de direction est un flux en deux étapes (créer la revue, puis
// y ajouter des décisions) — le modal ne se ferme donc qu'à la fin
// explicite du flux (bouton "Terminé"), pas juste après la création de la
// revue, sinon l'étape des décisions serait inatteignable.
function fermerRevue() {
  revueOuverte.value = false;
  revueCreee.value = null;
  erreurRevue.value = null;
  nouvelleRevue.value = { date: "", lieu: "", periode_debut: "", periode_fin: "", participants: "" };
  // Une décision ajoutée pendant le flux de création n'apparaissait dans
  // aucune liste ensuite : recharger l'historique pour que la revue tout
  // juste créée (et ses décisions) apparaisse immédiatement dans le tableau.
  audits.charger();
}

// --- Fiche détail d'une revue existante (2026-09-19) ---
const detailOuvert = ref(false);
const chargementDetail = ref(false);
const erreurDetail = ref(null);
const commentaireEdite = ref("");
const actionEnCours = ref(false);

async function ouvrirDetail(revue) {
  detailOuvert.value = true;
  chargementDetail.value = true;
  erreurDetail.value = null;
  try {
    await audits.chargerRevueDetail(revue.id);
    commentaireEdite.value = audits.revueDetail?.commentaire_ia ?? "";
  } catch (e) {
    erreurDetail.value = e?.message ?? "Impossible de charger cette revue";
  } finally {
    chargementDetail.value = false;
  }
}
function fermerDetail() {
  detailOuvert.value = false;
  audits.revueDetail = null;
}

async function genererCommentaire() {
  actionEnCours.value = true;
  erreurDetail.value = null;
  const avant = audits.revueDetail.commentaire_ia;
  try {
    await audits.genererCommentaire(audits.revueDetail.id);
    // Le service ne remplace jamais commentaire_ia si l'assistant est
    // indisponible ("mode dégradé" — voir app/services/assistance/client.py,
    // même principe que AssistantDocumentaireView.vue) : un texte inchangé
    // après l'appel est le seul signal côté client, la route ne remonte pas
    // `disponible`.
    if (audits.revueDetail.commentaire_ia === avant) {
      erreurDetail.value = "L'assistant est indisponible pour le moment. Réessayez plus tard, ou rédigez le commentaire manuellement ci-dessous.";
    }
    commentaireEdite.value = audits.revueDetail.commentaire_ia ?? "";
  } catch (e) {
    erreurDetail.value = e?.message ?? "Impossible de générer le commentaire";
  } finally {
    actionEnCours.value = false;
  }
}
async function enregistrerCommentaire() {
  actionEnCours.value = true;
  erreurDetail.value = null;
  try {
    await audits.modifierCommentaire(audits.revueDetail.id, commentaireEdite.value);
  } catch (e) {
    erreurDetail.value = e?.message ?? "Impossible d'enregistrer le commentaire";
  } finally {
    actionEnCours.value = false;
  }
}
async function validerCommentaire() {
  actionEnCours.value = true;
  erreurDetail.value = null;
  try {
    await audits.validerCommentaire(audits.revueDetail.id);
  } catch (e) {
    erreurDetail.value = e?.message ?? "Impossible de valider le commentaire";
  } finally {
    actionEnCours.value = false;
  }
}
async function solderDecision(decisionId) {
  erreurDetail.value = null;
  try {
    await audits.solderDecision(decisionId);
  } catch (e) {
    erreurDetail.value = e?.message ?? "Impossible de solder cette décision";
  }
}

const pdfRevueEnCours = ref(null);
async function telechargerRevue(revue) {
  pdfRevueEnCours.value = revue.id;
  try {
    await telechargerPdf(`/api/v1/revues/${revue.id}/export-pdf`, `${revue.reference ?? "revue-" + revue.id}.pdf`);
  } catch (e) {
    audits.erreur = e?.message ?? "Téléchargement du PDF impossible";
  } finally {
    pdfRevueEnCours.value = null;
  }
}

function nomUtilisateur(id) {
  const u = audits.utilisateurs.find((u) => u.id === id);
  return u ? `${u.prenom} ${u.nom}` : `Utilisateur #${id}`;
}
</script>

<template>
  <div>
    <div v-if="audits.erreur" class="banner err">{{ audits.erreur }}</div>

    <div class="card">
      <div class="ch"><Icone nom="list" /><h3>Audit interne</h3>
        <span v-if="!audits.campagne" class="r" role="button" tabindex="0" @click="audits.ouvrirCampagne" @keydown.enter="audits.ouvrirCampagne">Ouvrir une campagne</span>
      </div>
      <div class="cb" v-if="audits.campagne">
        <div class="statbar" style="margin-bottom: 12px">
          <span>Maturité du système</span>
          <span class="v">{{ audits.campagne.taux_conformite_pourcent?.toFixed(0) ?? "—" }} % — {{ audits.campagne.interpretation }}</span>
        </div>
        <template v-for="(exigences, chapitre) in exigencesParChapitre" :key="chapitre">
          <div class="sec" style="margin: 10px 0 6px">{{ chapitre }}</div>
          <ul class="cl">
            <li v-for="e in exigences" :key="e.id">
              <span class="tx">{{ e.libelle }}</span>
              <span class="tri">
                <button class="n" :class="{ on: cotationDe(e.id) === 0 }" @click="audits.coter(e.id, 0)">0</button>
                <button class="s" :class="{ on: cotationDe(e.id) === 1 }" @click="audits.coter(e.id, 1)">1</button>
                <button class="c" :class="{ on: cotationDe(e.id) === 2 }" @click="audits.coter(e.id, 2)">2</button>
              </span>
            </li>
          </ul>
        </template>
        <div style="display: flex; gap: 8px; margin-top: 10px">
          <button v-if="audits.campagne.statut !== 'cloturee'" class="btn pri" style="width: auto" @click="audits.cloturerCampagne">
            Clôturer et générer le rapport
          </button>
          <button class="btn gh" style="width: auto" :disabled="pdfEnCours" @click="telechargerRapportCampagne">
            <Icone nom="dl" taille="sm" />Rapport PDF
          </button>
        </div>
      </div>
    </div>

    <div class="card">
      <div class="ch"><Icone nom="check" /><h3>Revue de direction</h3>
        <span v-if="!revueOuverte && peutGererRevues" class="r" role="button" tabindex="0" @click="revueOuverte = true" @keydown.enter="revueOuverte = true">Nouvelle revue</span>
      </div>
      <table>
        <thead><tr><th>Référence</th><th>Date</th><th>Période</th><th>Commentaire</th><th></th></tr></thead>
        <tbody>
          <tr v-for="r in audits.revues" :key="r.id" style="cursor: pointer" @click="ouvrirDetail(r)">
            <td><b>{{ r.reference ?? `Revue #${r.id}` }}</b></td>
            <td>{{ formaterDateCivile(r.date) }}</td>
            <td>{{ formaterDateCivile(r.periode_debut) }} → {{ formaterDateCivile(r.periode_fin) }}</td>
            <td>
              <span v-if="!r.commentaire_ia" class="tag t-gy">Non généré</span>
              <span v-else-if="r.commentaire_valide" class="tag t-gr">Validé</span>
              <span v-else class="tag t-or">Brouillon</span>
            </td>
            <td style="text-align: right">
              <button class="btn gh sm" style="width: auto" :disabled="pdfRevueEnCours === r.id" @click.stop="telechargerRevue(r)">
                <Icone nom="dl" taille="sm" />PDF
              </button>
            </td>
          </tr>
          <tr v-if="!audits.chargement && !audits.revues.length"><td colspan="5" style="color: var(--mut)">Aucune revue de direction enregistrée.</td></tr>
        </tbody>
      </table>
    </div>

    <Modal v-if="revueOuverte" titre="Revue de direction" @fermer="fermerRevue">
      <template v-if="!revueCreee">
        <div class="grid2">
          <div>
            <label class="f">Date</label><input v-model="nouvelleRevue.date" type="date" class="inp" />
            <label class="f">Lieu</label><input v-model="nouvelleRevue.lieu" class="inp" />
          </div>
          <div>
            <label class="f">Période — début</label><input v-model="nouvelleRevue.periode_debut" type="date" class="inp" />
            <label class="f">Période — fin</label><input v-model="nouvelleRevue.periode_fin" type="date" class="inp" />
          </div>
        </div>
        <label class="f">Participants</label><input v-model="nouvelleRevue.participants" class="inp" />
        <div v-if="erreurRevue" class="banner err" style="margin-top: 8px">{{ erreurRevue }}</div>
        <div style="display: flex; gap: 8px; margin-top: 10px">
          <button class="btn pri" style="width: auto" @click="soumettreRevue">Enregistrer</button>
          <button class="btn gh" style="width: auto" @click="fermerRevue">Annuler</button>
        </div>
      </template>
      <template v-else>
        <div class="banner info" style="margin-bottom: 10px">Revue {{ revueCreee.reference ?? "créée" }} enregistrée. Ajoutez les décisions ci-dessous.</div>
        <div class="grid2">
          <input v-model="nouvelleDecision.libelle" class="inp" placeholder="Décision" />
          <select v-model="nouvelleDecision.responsable_id" class="inp">
            <option value="" disabled>Responsable…</option>
            <option v-for="u in audits.utilisateurs" :key="u.id" :value="u.id">{{ u.prenom }} {{ u.nom }}</option>
          </select>
        </div>
        <input v-model="nouvelleDecision.echeance" type="date" class="inp" style="margin-top: 8px" />
        <div style="display: flex; gap: 8px; margin-top: 10px">
          <button class="btn pri" style="width: auto" @click="ajouterDecision">Ajouter la décision</button>
          <button class="btn gh" style="width: auto" @click="fermerRevue">Terminé</button>
        </div>
      </template>
    </Modal>

    <Modal
      v-if="detailOuvert"
      :titre="audits.revueDetail ? `Revue ${audits.revueDetail.reference ?? '#' + audits.revueDetail.id}` : 'Revue de direction'"
      @fermer="fermerDetail"
    >
      <div v-if="chargementDetail" class="skel" style="height: 160px"></div>
      <div v-else-if="erreurDetail && !audits.revueDetail" class="banner err">{{ erreurDetail }}</div>
      <template v-else-if="audits.revueDetail">
        <div class="kv"><span>Date</span><b>{{ formaterDateCivile(audits.revueDetail.date) }}</b></div>
        <div class="kv"><span>Période</span><b>{{ formaterDateCivile(audits.revueDetail.periode_debut) }} → {{ formaterDateCivile(audits.revueDetail.periode_fin) }}</b></div>
        <div class="kv" v-if="audits.revueDetail.lieu"><span>Lieu</span><b>{{ audits.revueDetail.lieu }}</b></div>
        <div class="kv" v-if="audits.revueDetail.participants"><span>Participants</span><b>{{ audits.revueDetail.participants }}</b></div>

        <div class="sec" style="margin-top: 14px">COMMENTAIRE DE SYNTHÈSE</div>
        <p style="font-size: 12px; color: var(--mut); margin: 4px 0 8px">
          Pré-rédigé à partir des indicateurs de la période ; à relire et valider avant export — jamais inclus dans le PDF tant qu'il n'est pas validé.
        </p>
        <textarea
          v-model="commentaireEdite"
          class="inp"
          rows="6"
          placeholder="Aucun commentaire pour l'instant — cliquez sur Générer."
        ></textarea>
        <div v-if="audits.revueDetail.commentaire_valide" class="banner info" style="margin-top: 6px">Commentaire validé — inclus dans l'export PDF.</div>
        <div style="display: flex; gap: 8px; margin-top: 8px; flex-wrap: wrap">
          <button class="btn gh sm" style="width: auto" :disabled="actionEnCours" @click="genererCommentaire">
            {{ audits.revueDetail.commentaire_ia ? "Régénérer" : "Générer" }}
          </button>
          <button class="btn gh sm" style="width: auto" :disabled="actionEnCours" @click="enregistrerCommentaire">Enregistrer le texte</button>
          <button
            v-if="commentaireEdite && !audits.revueDetail.commentaire_valide"
            class="btn pri sm"
            style="width: auto"
            :disabled="actionEnCours"
            @click="validerCommentaire"
          >Valider</button>
        </div>

        <div class="sec" style="margin-top: 14px">DÉCISIONS</div>
        <div v-for="d in audits.revueDetail.decisions" :key="d.id" class="kv">
          <span>{{ d.libelle }} — {{ nomUtilisateur(d.responsable_id) }} · {{ formaterDateCivile(d.echeance) }}</span>
          <span style="display: flex; align-items: center; gap: 8px">
            <span class="tag" :class="d.statut === 'soldee' ? 't-gr' : 't-or'">{{ d.statut === 'soldee' ? 'Soldée' : 'Ouverte' }}</span>
            <button v-if="d.statut !== 'soldee'" class="btn gh sm" style="width: auto" @click="solderDecision(d.id)">Solder</button>
          </span>
        </div>
        <p v-if="!audits.revueDetail.decisions.length" style="color: var(--mut); font-size: 12.5px">Aucune décision enregistrée pour cette revue.</p>

        <div v-if="erreurDetail" class="banner err" style="margin-top: 10px">{{ erreurDetail }}</div>

        <div style="display: flex; gap: 8px; margin-top: 12px">
          <button class="btn gh" style="width: auto" :disabled="pdfRevueEnCours === audits.revueDetail.id" @click="telechargerRevue(audits.revueDetail)">
            <Icone nom="dl" taille="sm" />Télécharger le PDF
          </button>
          <button class="btn gh" style="width: auto" @click="fermerDetail">Fermer</button>
        </div>
      </template>
    </Modal>
  </div>
</template>

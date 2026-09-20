<script setup>
/**
 * EPI antichute — vue desktop (maquette #p-epi).
 *
 * Recherche + pagination ajoutées le 2026-09-10 (revue d'ensemble), comme
 * les autres tableaux desktop.
 *
 * Création/affectation/retrait/réforme ajoutés le 2026-09-19 (revue de
 * compatibilité front/back, "tu corriges tout") : les quatre routes
 * existaient côté serveur depuis le prompt 2.1 (POST /epi, PATCH
 * .../affectation, POST .../retirer, POST .../reformer), l'écran n'étant
 * jusqu'ici qu'un tableau de lecture. Réservé à GERER_EPI
 * (referent_sheq/administrateur, backend/app/core/permissions.py) — même
 * garde locale que EpiView.vue mobile, pour ne pas proposer des actions
 * qui échoueraient en 403 à un responsable simple consultant.
 */
import { computed, onMounted, ref } from "vue";
import BarrePagination from "../components/BarrePagination.vue";
import Icone from "../components/Icone.vue";
import Modal from "../components/Modal.vue";
import ModalConfirmation from "../components/ModalConfirmation.vue";
import { useRechercheEtPagination } from "../composables/useRechercheEtPagination";
import { useAuthStore } from "../stores/auth";
import { useEpiStore } from "../stores/epi";
import { formaterDateCivile, joursRestantsCivil } from "../utils/dates";

const auth = useAuthStore();
const epi = useEpiStore();

onMounted(() => epi.charger());

const peutGerer = computed(() => ["referent_sheq", "administrateur"].includes(auth.utilisateur?.role));

const LIBELLES_TYPE = {
  harnais: "Harnais complet",
  longe: "Longe",
  antichute_mobile: "Antichute mobile",
  casque: "Casque",
  connecteur: "Connecteur",
  ligne_de_vie: "Ligne de vie",
};

const enService = computed(() => epi.liste.filter((e) => e.statut === "en_service").length);
// `statut === "a_verifier"` compte comme "dû"/"bloquant" même quand la date de
// prochaine vérification reste lointaine : un contrôle NON CONFORME (avant
// utilisation ou périodique) ne rapproche pas forcément cette date (voir
// services/epi_service.py, enregistrer_verification_avant_utilisation) —
// bug réel trouvé en vérifiant en conditions réelles ce lot-ci.
const dues = computed(() => epi.liste.filter((e) => e.statut === "a_verifier" || (joursRestants(e.prochaine_verification) !== null && joursRestants(e.prochaine_verification) <= 7 && e.statut !== "reforme" && e.statut !== "retire")));
const reformes = computed(() => epi.liste.filter((e) => e.statut === "reforme").length);
const bloquants = computed(() => epi.liste.filter((e) => e.statut === "a_verifier" || (joursRestants(e.prochaine_verification) !== null && joursRestants(e.prochaine_verification) < 0)));

const joursRestants = joursRestantsCivil;
const formaterDate = formaterDateCivile;

function correspond(e, terme) {
  return (
    String(e.numero ?? "").toLowerCase().includes(terme) ||
    (LIBELLES_TYPE[e.type] ?? e.type ?? "").toLowerCase().includes(terme) ||
    (e.marque_modele ?? "").toLowerCase().includes(terme) ||
    (e.porteur_id ? (epi.nomUtilisateur(e.porteur_id) ?? "") : "").toLowerCase().includes(terme)
  );
}
const { recherche, page, totalPages, resultats, elementsPage, allerPage } =
  useRechercheEtPagination(computed(() => epi.liste), correspond, 12);

function statutTag(item) {
  if (item.statut === "reforme") return { classe: "t-gy", libelle: `Réformé${item.motif_reforme ? " — " + item.motif_reforme.slice(0, 30) : ""}` };
  if (item.statut === "retire") return { classe: "t-gy", libelle: "Retiré" };
  // Voir la même correction dans EpiView.vue (mobile) : `a_verifier` doit
  // primer sur la date, un contrôle non conforme ne la rapproche pas.
  if (item.statut === "a_verifier") return { classe: "t-red", libelle: "À vérifier" };
  const jours = joursRestants(item.prochaine_verification);
  if (jours !== null && jours < 0) return { classe: "t-red", libelle: "À vérifier" };
  if (jours !== null && jours <= 7) return { classe: "t-or", libelle: `J−${jours}` };
  return { classe: "t-gr", libelle: "En service" };
}

const CHAMPS_VIERGES = {
  type: "",
  marque_modele: "",
  date_fabrication: "",
  date_mise_service: new Date().toISOString().slice(0, 10),
  date_limite: "",
  porteur_id: "",
};

const formulaireOuvert = ref(false);
const nouveau = ref({ ...CHAMPS_VIERGES });
const erreurFormulaire = ref(null);

async function soumettre() {
  erreurFormulaire.value = null;
  try {
    await epi.creer({
      ...nouveau.value,
      date_fabrication: nouveau.value.date_fabrication || null,
      porteur_id: nouveau.value.porteur_id ? Number(nouveau.value.porteur_id) : null,
    });
    formulaireOuvert.value = false;
    nouveau.value = { ...CHAMPS_VIERGES };
  } catch (e) {
    erreurFormulaire.value = e?.message ?? "Impossible d'enregistrer cet EPI";
  }
}

const affectationEnCours = ref(null);
const porteurChoisi = ref("");

function ouvrirAffectation(item) {
  affectationEnCours.value = item.id;
  porteurChoisi.value = item.porteur_id ? String(item.porteur_id) : "";
}
async function confirmerAffectation() {
  try {
    await epi.affecter(affectationEnCours.value, porteurChoisi.value ? Number(porteurChoisi.value) : null);
    affectationEnCours.value = null;
  } catch (e) {
    epi.erreur = e?.message ?? "Impossible de modifier l'affectation";
  }
}

const aRetirer = ref(null);
async function confirmerRetrait() {
  const item = aRetirer.value;
  aRetirer.value = null;
  try {
    await epi.retirer(item.id);
  } catch (e) {
    epi.erreur = e?.message ?? "Impossible de retirer cet EPI";
  }
}

const aReformer = ref(null);
const motifReforme = ref("");
const erreurReforme = ref(null);
function ouvrirReforme(item) {
  aReformer.value = item;
  motifReforme.value = "";
  erreurReforme.value = null;
}
async function confirmerReforme() {
  if (!motifReforme.value.trim()) {
    erreurReforme.value = "Le motif de réforme est obligatoire.";
    return;
  }
  try {
    await epi.reformer(aReformer.value.id, motifReforme.value.trim());
    aReformer.value = null;
  } catch (e) {
    erreurReforme.value = e?.message ?? "Impossible de réformer cet EPI";
  }
}
</script>

<template>
  <div>
    <div v-if="epi.erreur" class="banner err">{{ epi.erreur }}</div>

    <div class="mets" style="grid-template-columns: repeat(3, 1fr)">
      <div class="met">
        <div class="met-hd"><span class="ic m-gr"><Icone nom="vest" taille="sm" /></span>EPI en service</div>
        <div class="v">{{ enService }}</div>
        <div class="t flat">sur {{ epi.liste.length }} enregistrés</div>
      </div>
      <div class="met">
        <div class="met-hd"><span class="ic m-or"><Icone nom="clock" taille="sm" /></span>Vérifications dues</div>
        <div class="v">{{ dues.length }}</div>
        <div class="t" :class="bloquants.length ? 'down' : 'flat'">dont {{ bloquants.length }} dépassée{{ bloquants.length > 1 ? "s" : "" }}</div>
      </div>
      <div class="met">
        <div class="met-hd"><span class="ic m-bl"><Icone nom="shield" taille="sm" /></span>Réformés</div>
        <div class="v">{{ reformes }}</div>
        <div class="t flat">équipements retirés du parc</div>
      </div>
    </div>

    <div v-if="bloquants.length" class="banner err">
      <Icone nom="lock" taille="sm" style="margin-top: 1px" />
      <div><b>{{ bloquants.length }} EPI dépassé{{ bloquants.length > 1 ? "s" : "" }} bloque{{ bloquants.length > 1 ? "nt" : "" }} la délivrance des permis</b> pour son ou leurs porteurs — contrôle croisé automatique.</div>
    </div>

    <Modal v-if="formulaireOuvert" titre="Nouvel EPI" @fermer="formulaireOuvert = false">
      <div class="grid2">
        <div>
          <label class="f">Type</label>
          <select v-model="nouveau.type" class="inp">
            <option value="" disabled>Choisir…</option>
            <option v-for="(libelle, valeur) in LIBELLES_TYPE" :key="valeur" :value="valeur">{{ libelle }}</option>
          </select>
          <label class="f">Marque / modèle</label><input v-model="nouveau.marque_modele" class="inp" />
          <label class="f">Date de fabrication</label><input v-model="nouveau.date_fabrication" type="date" class="inp" />
        </div>
        <div>
          <label class="f">Mise en service</label><input v-model="nouveau.date_mise_service" type="date" class="inp" />
          <label class="f">Fin de vie</label><input v-model="nouveau.date_limite" type="date" class="inp" />
          <label class="f">Porteur (facultatif)</label>
          <select v-model="nouveau.porteur_id" class="inp">
            <option value="">Non affecté</option>
            <option v-for="u in epi.utilisateurs" :key="u.id" :value="u.id">{{ u.prenom }} {{ u.nom }}</option>
          </select>
        </div>
      </div>
      <div v-if="erreurFormulaire" class="banner err" style="margin-top: 8px">{{ erreurFormulaire }}</div>
      <div style="display: flex; gap: 8px; margin-top: 10px">
        <button class="btn pri" style="width: auto" @click="soumettre">Enregistrer</button>
        <button class="btn gh" style="width: auto" @click="formulaireOuvert = false">Annuler</button>
      </div>
    </Modal>

    <div class="card">
      <div class="ch">
        <h3>EPI enregistrés</h3>
        <span style="flex: 1"></span>
        <div class="srch">
          <Icone nom="search" taille="sm" />
          <input v-model="recherche" placeholder="Rechercher un EPI, un porteur…" />
        </div>
        <span
          v-if="peutGerer"
          class="r"
          style="cursor: pointer"
          role="button"
          tabindex="0"
          @click="formulaireOuvert = true"
          @keydown.enter="formulaireOuvert = true"
        >Nouvel EPI</span>
      </div>
      <table>
        <thead>
          <tr>
            <th>N°</th><th>Type</th><th>Marque / modèle</th><th>Affecté à</th><th>Mise en service</th>
            <th>Dernière vérif.</th><th>Prochaine</th><th>Fin de vie</th><th>Statut</th>
            <th v-if="peutGerer"></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in elementsPage" :key="item.id">
            <td><b>{{ item.numero }}</b></td>
            <td>{{ LIBELLES_TYPE[item.type] ?? item.type }}</td>
            <td>{{ item.marque_modele }}</td>
            <td>
              <template v-if="affectationEnCours === item.id">
                <select v-model="porteurChoisi" class="inp" style="width: 150px; padding: 4px 6px; display: inline-block">
                  <option value="">Non affecté</option>
                  <option v-for="u in epi.utilisateurs" :key="u.id" :value="u.id">{{ u.prenom }} {{ u.nom }}</option>
                </select>
                <button class="btn pri sm" style="width: auto; margin-left: 4px" @click="confirmerAffectation">OK</button>
              </template>
              <template v-else>{{ item.porteur_id ? epi.nomUtilisateur(item.porteur_id) ?? `Utilisateur #${item.porteur_id}` : "—" }}</template>
            </td>
            <td>{{ formaterDate(item.date_mise_service) }}</td>
            <td>{{ formaterDate(item.derniere_verification) }}</td>
            <td :style="statutTag(item).classe === 't-red' ? 'color:var(--red);font-weight:650' : statutTag(item).classe === 't-or' ? 'color:var(--orange);font-weight:650' : ''">
              {{ formaterDate(item.prochaine_verification) }}
            </td>
            <td>{{ formaterDate(item.date_limite) }}</td>
            <td><span class="tag" :class="statutTag(item).classe">{{ statutTag(item).libelle }}</span></td>
            <td v-if="peutGerer" style="text-align: right; white-space: nowrap">
              <template v-if="item.statut !== 'reforme'">
                <button class="btn gh sm" style="width: auto" @click="ouvrirAffectation(item)">Affecter</button>
                <button v-if="item.statut !== 'retire'" class="btn gh sm" style="width: auto; margin-left: 6px" @click="aRetirer = item">Retirer</button>
                <button class="btn gh sm" style="width: auto; margin-left: 6px" @click="ouvrirReforme(item)">Réformer</button>
              </template>
            </td>
          </tr>
          <tr v-if="!epi.chargement && !epi.liste.length"><td :colspan="peutGerer ? 10 : 9" style="color: var(--mut)">Aucun EPI enregistré.</td></tr>
          <tr v-if="epi.liste.length && !resultats.length"><td :colspan="peutGerer ? 10 : 9" style="color: var(--mut)">Aucun EPI ne correspond à la recherche.</td></tr>
        </tbody>
      </table>
      <BarrePagination :page="page" :total-pages="totalPages" @changer="allerPage">
        {{ resultats.length }} sur {{ epi.liste.length }} EPI
      </BarrePagination>
    </div>

    <ModalConfirmation
      v-if="aRetirer"
      titre="Retirer cet EPI du service"
      :message="`Retirer ${aRetirer.numero} du service ? Action réversible — une nouvelle vérification conforme le remet en service.`"
      libelle-confirmer="Retirer"
      @confirmer="confirmerRetrait"
      @annuler="aRetirer = null"
    />

    <Modal v-if="aReformer" titre="Réformer cet EPI" @fermer="aReformer = null">
      <p style="font-size: 13px; color: var(--mut); margin-bottom: 8px">
        Réformer {{ aReformer.numero }} est irréversible : aucune opération ne pourra le remettre en service.
      </p>
      <label class="f">Motif de réforme</label>
      <input v-model="motifReforme" class="inp" placeholder="Usure, choc, fin de vie…" />
      <div v-if="erreurReforme" class="banner err" style="margin-top: 8px">{{ erreurReforme }}</div>
      <div style="display: flex; gap: 8px; margin-top: 10px">
        <button class="btn pri" style="width: auto" @click="confirmerReforme">Réformer</button>
        <button class="btn gh" style="width: auto" @click="aReformer = null">Annuler</button>
      </div>
    </Modal>
  </div>
</template>

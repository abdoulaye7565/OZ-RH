<script setup>
/**
 * Satisfaction client — vue desktop (maquette #p-satis).
 *
 * Écarts assumés :
 * 1. La maquette n'a pas de formulaire de création visible — ajouté un
 *    formulaire repliable ("Nouvelle enquête"), même principe que les
 *    autres écrans desktop (Parc, Déchets).
 * 2. La moyenne par critère et la moyenne globale n'ont pas de route
 *    d'agrégation dédiée : calculées côté client à partir de
 *    GET /satisfaction/reponses (nouvelle route de liste ajoutée pour ce
 *    besoin, en plus de /a-traiter qui ne couvre que les réponses à
 *    analyser — voir stores/satisfaction.js).
 * 3. "Suite donnée" (dernière colonne de la table "Enquêtes envoyées") ne
 *    référence pas l'action corrective réellement créée (pas de route pour
 *    retrouver une action à partir d'une réponse) : affiche seulement si
 *    une analyse est requise, pas le numéro de l'action.
 */
import { computed, onMounted, ref } from "vue";
import BarrePagination from "../components/BarrePagination.vue";
import Icone from "../components/Icone.vue";
import Modal from "../components/Modal.vue";
import { useRechercheEtPagination } from "../composables/useRechercheEtPagination";
import { useSatisfactionStore } from "../stores/satisfaction";

const satisfaction = useSatisfactionStore();
onMounted(() => satisfaction.charger());

function correspond(e, terme) {
  return e.client?.toLowerCase().includes(terme) || e.intervention?.toLowerCase().includes(terme);
}
const { recherche, page, totalPages, resultats, elementsPage, allerPage } =
  useRechercheEtPagination(computed(() => satisfaction.enquetes), correspond, 15);

const COULEUR_BARRE = ["g", "gd", "g", "g", "gd", "g"];

function couleurBarre(index) {
  return COULEUR_BARRE[index % COULEUR_BARRE.length];
}

const tauxReponse = computed(() => {
  if (!satisfaction.enquetes.length) return 0;
  return Math.round((satisfaction.enquetes.filter((e) => e.repondu).length / satisfaction.enquetes.length) * 100);
});

const RECOMMANDATION_LIBELLE = { oui_certainement: "Oui, certainement", probablement: "Probablement", non: "Non" };

function noteCouleur(note) {
  if (note <= 2) return "t-red";
  if (note <= 3) return "t-or";
  return "t-gr";
}

const formulaireOuvert = ref(false);
const nouveau = ref({ client: "", site_id: "", intervention: "", technicien_id: "" });
const erreurFormulaire = ref(null);
const lienGenere = ref(null);

async function soumettre() {
  erreurFormulaire.value = null;
  try {
    const donnees = { client: nouveau.value.client, intervention: nouveau.value.intervention };
    if (nouveau.value.site_id) donnees.site_id = Number(nouveau.value.site_id);
    if (nouveau.value.technicien_id) donnees.technicien_id = Number(nouveau.value.technicien_id);
    const enquete = await satisfaction.creerEnquete(donnees);
    // Le modal se ferme après l'action (2026-09-09), mais le lien généré
    // reste affiché au niveau de la page — sinon l'administrateur n'aurait
    // aucune occasion de le copier avant qu'il disparaisse avec le modal.
    lienGenere.value = `${window.location.origin}/satisfaction/${enquete.jeton}`;
    nouveau.value = { client: "", site_id: "", intervention: "", technicien_id: "" };
    formulaireOuvert.value = false;
  } catch (e) {
    erreurFormulaire.value = e?.message ?? "Impossible de créer cette enquête";
  }
}
</script>

<template>
  <div>
    <div v-if="satisfaction.erreur" class="banner err">{{ satisfaction.erreur }}</div>
    <div v-if="lienGenere" class="banner info">
      <Icone nom="check" taille="sm" style="margin-top: 1px" />
      <div>Enquête créée. Lien à transmettre au client : <b>{{ lienGenere }}</b></div>
    </div>

    <div class="grid2" style="grid-template-columns: 1fr 1fr">
      <div class="card">
        <div class="ch"><Icone nom="star" style="color: var(--gold)" /><h3>Satisfaction moyenne</h3><span class="r">{{ satisfaction.reponses.length }} réponses</span></div>
        <div class="cb">
          <div v-if="satisfaction.moyenneGlobale === null" style="color: var(--mut); font-size: 12.5px">Aucune réponse reçue pour l'instant.</div>
          <template v-else>
            <div style="display: flex; align-items: baseline; gap: 10px; margin-bottom: 14px">
              <span style="font-size: 38px; font-weight: 750; letter-spacing: -1.6px">{{ satisfaction.moyenneGlobale.toFixed(1) }}</span>
              <span style="color: var(--mut); font-size: 13px">/ 5 · taux de réponse {{ tauxReponse }} %</span>
            </div>
            <div v-for="(critere, i) in Object.keys(satisfaction.moyenneParCritere)" :key="critere" style="margin-bottom: 10px">
              <div style="display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 4px">
                <b>{{ critere }}</b><span style="color: var(--mut)">{{ satisfaction.moyenneParCritere[critere].toFixed(1) }}</span>
              </div>
              <div class="trk"><div class="fl" :class="couleurBarre(i)" :style="{ width: `${(satisfaction.moyenneParCritere[critere] / 5) * 100}%` }"></div></div>
            </div>
          </template>
        </div>
      </div>

      <div class="card">
        <div class="ch"><Icone nom="alert" style="color: var(--orange)" /><h3>Retours nécessitant une action</h3></div>
        <div class="cb">
          <div v-if="satisfaction.aTraiter.length" class="banner err" style="margin-bottom: 12px">
            <Icone nom="alert" taille="sm" style="margin-top: 1px" />
            <div><b>{{ satisfaction.aTraiter.length }} réponse{{ satisfaction.aTraiter.length > 1 ? "s" : "" }} à 2 étoiles ou moins</b> — une analyse est requise.</div>
          </div>
          <p v-else style="color: var(--mut); font-size: 12.5px">Aucun retour n'exige d'analyse pour l'instant.</p>
          <table>
            <tbody>
              <tr v-for="r in satisfaction.aTraiter" :key="r.id">
                <td>
                  <div><b>{{ r.remarques || "Sans commentaire" }}</b><div class="sub">{{ RECOMMANDATION_LIBELLE[r.recommandation] }}</div></div>
                </td>
                <td style="text-align: right">
                  <span class="tag" :class="noteCouleur(Math.min(...r.notes.map((n) => n.note)))">{{ Math.min(...r.notes.map((n) => n.note)) }} / 5</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <Modal v-if="formulaireOuvert" titre="Nouvelle enquête" @fermer="formulaireOuvert = false">
      <div class="grid2">
        <div>
          <label class="f">Client</label><input v-model="nouveau.client" class="inp" />
          <label class="f">Intervention</label><input v-model="nouveau.intervention" class="inp" placeholder="Installation liaison, maintenance…" />
        </div>
        <div>
          <label class="f">Site (facultatif)</label>
          <select v-model="nouveau.site_id" class="inp">
            <option value="">Aucun</option>
            <option v-for="s in satisfaction.sites" :key="s.id" :value="s.id">{{ s.nom }}</option>
          </select>
          <label class="f">Technicien (facultatif)</label>
          <select v-model="nouveau.technicien_id" class="inp">
            <option value="">Aucun</option>
            <option v-for="u in satisfaction.utilisateurs.filter((u) => u.role === 'technicien')" :key="u.id" :value="u.id">{{ u.prenom }} {{ u.nom }}</option>
          </select>
        </div>
      </div>
      <div v-if="erreurFormulaire" class="banner err" style="margin-top: 8px">{{ erreurFormulaire }}</div>
      <div style="display: flex; gap: 8px; margin-top: 10px">
        <button class="btn pri" style="width: auto" @click="soumettre">Envoyer l'enquête</button>
        <button class="btn gh" style="width: auto" @click="formulaireOuvert = false">Annuler</button>
      </div>
    </Modal>

    <div class="card">
      <div class="ch">
        <h3>Enquêtes envoyées</h3>
        <span style="flex: 1"></span>
        <div class="srch">
          <Icone nom="search" taille="sm" />
          <input v-model="recherche" placeholder="Rechercher un client, une intervention…" />
        </div>
        <span
          class="r"
          style="cursor: pointer"
          role="button"
          tabindex="0"
          @click="formulaireOuvert = true"
          @keydown.enter="formulaireOuvert = true"
        >Nouvelle enquête</span>
      </div>
      <table>
        <thead><tr><th>Client</th><th>Intervention</th><th>Envoyée</th><th>Réponse</th><th>Note</th><th>Suite donnée</th></tr></thead>
        <tbody>
          <tr v-for="e in elementsPage" :key="e.id">
            <td><b>{{ e.client }}</b></td>
            <td>{{ e.intervention }}</td>
            <td>{{ new Date(e.envoyee_le).toLocaleDateString("fr-FR") }}</td>
            <td>
              <span v-if="e.repondu" class="tag t-gr">Répondu</span>
              <span v-else class="tag t-gy">Sans réponse</span>
            </td>
            <td>
              <span v-if="satisfaction.reponseParEnquete(e.id)" class="tag" :class="noteCouleur(Math.round(satisfaction.reponseParEnquete(e.id).notes.reduce((a, n) => a + n.note, 0) / satisfaction.reponseParEnquete(e.id).notes.length))">
                {{ (satisfaction.reponseParEnquete(e.id).notes.reduce((a, n) => a + n.note, 0) / satisfaction.reponseParEnquete(e.id).notes.length).toFixed(1) }} / 5
              </span>
              <span v-else class="tag t-gy">—</span>
            </td>
            <td>
              <span v-if="satisfaction.reponseParEnquete(e.id)?.necessite_analyse" class="tag t-bl">Analyse requise</span>
              <span v-else class="tag t-gy">—</span>
            </td>
          </tr>
          <tr v-if="!satisfaction.chargement && !satisfaction.enquetes.length"><td colspan="6" style="color: var(--mut)">Aucune enquête envoyée.</td></tr>
          <tr v-if="satisfaction.enquetes.length && !resultats.length"><td colspan="6" style="color: var(--mut)">Aucune enquête ne correspond à la recherche.</td></tr>
        </tbody>
      </table>
      <BarrePagination :page="page" :total-pages="totalPages" @changer="allerPage">
        {{ resultats.length }} sur {{ satisfaction.enquetes.length }} enquêtes · toute note ≤ 2 déclenche une analyse
      </BarrePagination>
    </div>
  </div>
</template>

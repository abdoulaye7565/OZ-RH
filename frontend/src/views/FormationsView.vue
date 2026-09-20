<script setup>
/**
 * Formations — vue mobile (maquette #s-form).
 *
 * Écart assumé : le quiz de la maquette semble lié implicitement à "la"
 * séance du jour ; ici la séance est choisie explicitement (aucune séance
 * "du jour" déterminable sans ambiguïté côté API).
 */
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import Icone from "../components/Icone.vue";
import Modal from "../components/Modal.vue";
import BandeauReseau from "../components/BandeauReseau.vue";
import { useAuthStore } from "../stores/auth";
import { useFormationsStore } from "../stores/formations";
import { formaterDateCivile } from "../utils/dates";

const router = useRouter();
const auth = useAuthStore();
const formations = useFormationsStore();
onMounted(() => {
  formations.charger();
  formations.chargerQuestions();
});

const peutGerer = computed(() => ["referent_sheq", "administrateur"].includes(auth.utilisateur?.role));

const seancesAVenir = computed(() => [...formations.seances].filter((s) => s.statut === "planifiee").sort((a, b) => new Date(a.date) - new Date(b.date)));

function statutHabilitation(h) {
  return h.expiree ? { tag: "t-or", icone: "alert", libelle: "À RENOUVELER" } : { tag: "t-gr", icone: "check", libelle: "VALIDE" };
}

// --- Quiz ---
const seanceQuizId = ref("");
const reponses = ref({});
const resultatQuiz = ref(null);
const erreurQuiz = ref(null);

async function soumettreQuiz() {
  erreurQuiz.value = null;
  try {
    const payload = Object.entries(reponses.value).map(([question_id, reponse]) => ({ question_id: Number(question_id), reponse }));
    resultatQuiz.value = await formations.passerQuiz(Number(seanceQuizId.value), payload);
  } catch (e) {
    erreurQuiz.value = e?.message ?? "Impossible d'enregistrer vos réponses";
  }
}

// --- Formulaire nouvelle séance ---
const formulaireOuvert = ref(false);
const nouvelle = ref({ theme: "", date: "", lieu: "", animateur_id: "", competence_id: "" });
const erreurFormulaire = ref(null);

async function soumettreSeance() {
  erreurFormulaire.value = null;
  try {
    await formations.creerSeance({
      theme: nouvelle.value.theme,
      date: nouvelle.value.date,
      lieu: nouvelle.value.lieu,
      animateur_id: Number(nouvelle.value.animateur_id),
      competence_id: nouvelle.value.competence_id ? Number(nouvelle.value.competence_id) : null,
    });
    formulaireOuvert.value = false;
    nouvelle.value = { theme: "", date: "", lieu: "", animateur_id: "", competence_id: "" };
  } catch (e) {
    erreurFormulaire.value = e?.message ?? "Impossible d'enregistrer cette séance";
  }
}
</script>

<template>
  <div class="ecran-mobile">
    <BandeauReseau />
    <header class="hd">
      <button class="back" aria-label="Retour" @click="router.push({ name: 'menu' })"><Icone nom="back" /></button>
      <div>
        <h1>Formations</h1>
        <div class="sub">Compétences · planning · quiz</div>
      </div>
    </header>

    <div class="wrap">
      <div class="body">
        <div class="pad">
          <div v-if="formations.erreur" class="banner err">{{ formations.erreur }}</div>

          <div v-for="s in seancesAVenir" :key="s.id" class="row">
            <span class="lead bl"><Icone nom="cap" /></span>
            <div class="tx">
              <b>{{ s.theme }}</b>
              <div class="meta"><span>{{ formaterDateCivile(s.date) }}</span><span>{{ s.lieu }}</span><span>{{ formations.nomUtilisateur(s.animateur_id) ?? `Utilisateur #${s.animateur_id}` }}</span></div>
            </div>
          </div>

          <div class="sec" style="margin-top: 14px">MES COMPÉTENCES</div>
          <div v-for="h in formations.mesHabilitations" :key="h.id" class="row">
            <span class="lead" :class="statutHabilitation(h).tag === 't-or' ? 'or' : 'gr'"><Icone :nom="statutHabilitation(h).icone" /></span>
            <div class="tx">
              <b>{{ formations.nomCompetence(h.competence_id) ?? h.libelle_competence }}</b>
              <div class="meta"><span>Recyclage {{ formaterDateCivile(h.date_expiration) }}</span></div>
            </div>
            <span class="tag" :class="statutHabilitation(h).tag">{{ statutHabilitation(h).libelle }}</span>
          </div>
          <p v-if="!formations.mesHabilitations.length" style="font-size: 12px; color: var(--mut)">Aucune compétence enregistrée pour votre compte.</p>

          <div class="sec" style="margin-top: 14px">QUIZ DE SENSIBILISATION</div>
          <div class="card" style="padding: 13px">
            <label class="f">Séance concernée</label>
            <select v-model="seanceQuizId" class="inp">
              <option value="" disabled>Choisir…</option>
              <option v-for="s in formations.seances" :key="s.id" :value="s.id">{{ s.theme }} — {{ formaterDateCivile(s.date) }}</option>
            </select>

            <template v-if="seanceQuizId && !resultatQuiz">
              <div v-for="q in formations.questions" :key="q.id" style="margin-top: 12px">
                <p style="font-size: 13px; font-weight: 600; margin-bottom: 8px">{{ q.enonce }}</p>
                <button
                  v-for="c in q.choix"
                  :key="c.lettre"
                  class="btn gh"
                  :class="{ pri: reponses[q.id] === c.lettre }"
                  style="justify-content: flex-start; text-align: left; min-height: 42px; margin-bottom: 6px"
                  @click="reponses[q.id] = c.lettre"
                >
                  {{ c.lettre }}. {{ c.texte }}
                </button>
              </div>
              <div v-if="erreurQuiz" class="banner err" style="margin-top: 8px">{{ erreurQuiz }}</div>
              <button class="btn pri" style="margin-top: 10px" :disabled="Object.keys(reponses).length < formations.questions.length" @click="soumettreQuiz">
                Valider mes réponses
              </button>
            </template>

            <p v-if="resultatQuiz" style="font-size: 12px; color: var(--mut); margin-top: 10px">
              Score : {{ resultatQuiz.score }}/{{ resultatQuiz.total_questions }} ·
              <b :style="resultatQuiz.reussi ? 'color:var(--green)' : 'color:var(--red)'">{{ resultatQuiz.reussi ? "Réussi" : "Non réussi" }}</b>
            </p>
          </div>

          <div v-if="peutGerer">
            <div style="height: 12px"></div>
            <button class="btn pri" @click="formulaireOuvert = true"><Icone nom="plus" taille="sm" />Nouvelle séance</button>
            <Modal v-if="formulaireOuvert" titre="Nouvelle séance" @fermer="formulaireOuvert = false">
              <label class="f">Thème</label>
              <input v-model="nouvelle.theme" class="inp" />
              <label class="f">Date</label>
              <input v-model="nouvelle.date" type="date" class="inp" />
              <label class="f">Lieu</label>
              <input v-model="nouvelle.lieu" class="inp" />
              <label class="f">Animateur</label>
              <select v-model="nouvelle.animateur_id" class="inp">
                <option value="" disabled>Choisir…</option>
                <option v-for="u in formations.utilisateurs" :key="u.id" :value="u.id">{{ u.prenom }} {{ u.nom }}</option>
              </select>
              <label class="f">Compétence liée (facultatif)</label>
              <select v-model="nouvelle.competence_id" class="inp">
                <option value="">Aucune</option>
                <option v-for="c in formations.competences" :key="c.id" :value="c.id">{{ c.libelle }}</option>
              </select>
              <div v-if="erreurFormulaire" class="banner err" style="margin-top: 8px">{{ erreurFormulaire }}</div>
              <div class="btnrow" style="margin-top: 10px">
                <button class="btn pri sm" style="width: auto" @click="soumettreSeance">Enregistrer</button>
                <button class="btn gh sm" style="width: auto" @click="formulaireOuvert = false">Annuler</button>
              </div>
            </Modal>
          </div>

          <div style="height: 56px"></div>
        </div>
      </div>
    </div>

    <nav class="tabs">
      <button class="tb" @click="router.push({ name: 'accueil' })"><Icone nom="home" />Accueil</button>
      <button class="tb" @click="router.push({ name: 'signalements' })"><Icone nom="alert" />Signaux</button>
      <button class="tb" @click="router.push({ name: 'slam' })"><Icone nom="climb" />SLAM</button>
      <button class="tb" @click="router.push({ name: 'tableau-de-bord' })"><Icone nom="chart" />Tableau</button>
      <button class="tb" @click="router.push({ name: 'menu' })"><Icone nom="grid" />Menu</button>
    </nav>
  </div>
</template>

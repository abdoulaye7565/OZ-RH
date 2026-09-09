<script setup>
/**
 * Questionnaire de satisfaction — vue publique, sans compte (maquette
 * #s-satis, section 5.3.6 "envoi par lien public sans compte", FOR-SHEQ-018).
 * Accessible via /satisfaction/:jeton, route volontairement hors
 * authentification (le jeton en est la seule protection, côté serveur).
 *
 * Écarts assumés face à la maquette :
 * 1. Le vrai référentiel a 6 critères (`CRITERES` dans
 *    satisfaction_service.py), pas 3 — rendus dynamiquement à partir de la
 *    réponse de GET /questionnaire/{jeton} plutôt que codés en dur.
 * 2. `ReponseEntree` exige une `recommandation` (3 valeurs FOR-SHEQ-018) que
 *    le fragment de maquette fourni ne montre pas explicitement — ajoutée
 *    comme un choix à 3 boutons, seule façon de satisfaire un champ
 *    obligatoire du vrai schéma sans le deviner côté serveur.
 */
import { onMounted, reactive, ref } from "vue";
import { useRoute } from "vue-router";
import Icone from "../components/Icone.vue";
import { useSatisfactionStore } from "../stores/satisfaction";

const route = useRoute();
const satisfaction = useSatisfactionStore();

const chargement = ref(true);
const erreurChargement = ref(null);
const questionnaire = ref(null);
const notes = reactive({});
const RECOMMANDATIONS = [
  { valeur: "oui_certainement", libelle: "Oui, certainement" },
  { valeur: "probablement", libelle: "Probablement" },
  { valeur: "non", libelle: "Non" },
];
const recommandation = ref(null);
const remarques = ref("");
const envoye = ref(false);
const erreurEnvoi = ref(null);

onMounted(async () => {
  try {
    questionnaire.value = await satisfaction.chargerQuestionnaire(route.params.jeton);
    for (const critere of questionnaire.value.criteres) notes[critere] = 0;
  } catch (e) {
    erreurChargement.value = e?.message ?? "Ce lien n'est plus valide ou a déjà été utilisé.";
  } finally {
    chargement.value = false;
  }
});

function noter(critere, valeur) {
  notes[critere] = valeur;
}

async function envoyer() {
  erreurEnvoi.value = null;
  try {
    await satisfaction.repondre(route.params.jeton, {
      notes: Object.entries(notes).map(([critere, note]) => ({ critere, note })),
      recommandation: recommandation.value,
      remarques: remarques.value || null,
    });
    envoye.value = true;
  } catch (e) {
    erreurEnvoi.value = e?.message ?? "Impossible d'enregistrer votre réponse — vérifiez que toutes les questions sont notées.";
  }
}
</script>

<template>
  <div class="ecran-mobile">
    <div class="net online"><Icone nom="wifi" taille="sm" />En ligne<span class="sp">Lien client</span></div>
    <header class="hd">
      <div class="mk">H</div>
      <div>
        <h1>Votre avis</h1>
        <div class="sub" v-if="questionnaire">Intervention du {{ questionnaire.intervention }} — {{ questionnaire.client }}</div>
      </div>
    </header>

    <div class="wrap">
      <div class="body">
        <div class="pad">
          <div v-if="chargement" class="skel" style="height: 64px"></div>
          <div v-else-if="erreurChargement" class="banner err">{{ erreurChargement }}</div>

          <template v-else-if="envoye">
            <div class="empty">
              <div class="ic"><Icone nom="check" taille="lg" /></div>
              <b>Merci pour votre retour</b>
            </div>
          </template>

          <template v-else-if="questionnaire">
            <p style="font-size: 13px; color: var(--mut); margin-bottom: 6px">Envoyé par SMS ou QR code — sans compte à créer.</p>

            <div v-for="critere in questionnaire.criteres" :key="critere">
              <label class="f">{{ critere }}</label>
              <div class="stars">
                <button
                  v-for="i in 5"
                  :key="i"
                  type="button"
                  class="star"
                  :class="{ on: i <= notes[critere] }"
                  :aria-label="`${i} étoiles`"
                  @click="noter(critere, i)"
                >
                  <Icone nom="star" />
                </button>
              </div>
            </div>

            <label class="f">Recommanderiez-vous Hirondelles IT Lab ?</label>
            <div class="btnrow" style="margin-bottom: 8px">
              <button
                v-for="r in RECOMMANDATIONS"
                :key="r.valeur"
                type="button"
                class="btn sm"
                :class="recommandation === r.valeur ? 'pri' : 'gh'"
                style="width: auto"
                @click="recommandation = r.valeur"
              >
                {{ r.libelle }}
              </button>
            </div>

            <label class="f" for="sc1">Un commentaire ?</label>
            <textarea v-model="remarques" class="inp" id="sc1" placeholder="Vos remarques et suggestions…"></textarea>

            <div style="height: 13px"></div>
            <div v-if="erreurEnvoi" class="banner err" style="margin-bottom: 8px">{{ erreurEnvoi }}</div>
            <button class="btn gold" @click="envoyer">Envoyer mon avis</button>

            <div class="banner info" style="margin-top: 11px">
              <Icone nom="alert" taille="sm" style="margin-top: 1px" />
              <div>Toute note ≤ 2 alerte le référent SHEQ et ouvre une analyse.</div>
            </div>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

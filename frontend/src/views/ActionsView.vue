<script setup>
/**
 * Plan d'action — vue mobile (maquette #s-actions).
 *
 * Écart assumé : la création n'est proposée que depuis un risque (pas
 * signalement/inspection/écart d'audit/réponse de satisfaction) — ces
 * origines n'ont pas encore d'écran de détail d'où lancer "créer une action".
 * À étendre au fil des modules suivants.
 */
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import Icone from "../components/Icone.vue";
import Modal from "../components/Modal.vue";
import BandeauReseau from "../components/BandeauReseau.vue";
import { useAuthStore } from "../stores/auth";
import { useActionsStore } from "../stores/actions";
import { formaterDateCivile } from "../utils/dates";

const router = useRouter();
const auth = useAuthStore();
const actions = useActionsStore();
onMounted(() => actions.charger());

const filtre = ref("toutes");
const listeFiltree = computed(() => {
  if (filtre.value === "retard") return actions.liste.filter((a) => a.en_retard);
  if (filtre.value === "miennes") return actions.liste.filter((a) => a.responsable_id === auth.utilisateur?.id);
  return actions.liste;
});
const nombreEnRetard = computed(() => actions.liste.filter((a) => a.en_retard).length);
const nombreMiennes = computed(() => actions.liste.filter((a) => a.responsable_id === auth.utilisateur?.id).length);

function etat(a) {
  if (a.statut === "cloturee") return { lead: "gr", tag: "t-gr", icone: "check", libelle: "RÉALISÉE", barre: "g" };
  if (a.en_retard) return { lead: "red", tag: "t-red", icone: "clock", libelle: "RETARD", barre: "o" };
  return { lead: "gd", tag: "t-gd", icone: "shield", libelle: "EN COURS", barre: "gd" };
}

const formaterDate = formaterDateCivile;

const actionEnAction = ref(null);
const nouvelAvancement = ref(0);

function basculer(a) {
  if (actionEnAction.value === a.id) {
    actionEnAction.value = null;
  } else {
    actionEnAction.value = a.id;
    nouvelAvancement.value = a.avancement;
  }
}

async function enregistrerAvancement(a) {
  await actions.mettreAJourAvancement(a.id, Number(nouvelAvancement.value));
  actionEnAction.value = null;
}

async function cloturer(a) {
  await actions.changerStatut(a.id, "cloturee");
  actionEnAction.value = null;
}

// --- Formulaire de création ---
const formulaireOuvert = ref(false);
const nouvelle = ref({ libelle: "", risque_id: "", type_mesure: "corrective", responsable_id: "", echeance: "" });
const erreurFormulaire = ref(null);

async function soumettre() {
  erreurFormulaire.value = null;
  try {
    await actions.creer({
      libelle: nouvelle.value.libelle,
      risque_id: Number(nouvelle.value.risque_id),
      type_mesure: nouvelle.value.type_mesure,
      responsable_id: Number(nouvelle.value.responsable_id),
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
  <div class="ecran-mobile">
    <BandeauReseau />
    <header class="hd">
      <button class="back" aria-label="Retour" @click="router.push({ name: 'menu' })"><Icone nom="back" /></button>
      <div>
        <h1>Plan d'action</h1>
        <div class="sub">
          {{ actions.liste.length }} actions
          <template v-if="actions.synthese"> · {{ Math.round(actions.synthese.taux_avancement_global * 100) }} % réalisées</template>
        </div>
      </div>
    </header>

    <div class="wrap">
      <div class="body">
        <div class="pad">
          <div v-if="actions.erreur" class="banner err">{{ actions.erreur }}</div>

          <div class="segs" style="margin-bottom: 12px">
            <button class="seg" :class="{ on: filtre === 'toutes' }" @click="filtre = 'toutes'">Toutes</button>
            <button class="seg" :class="{ on: filtre === 'retard' }" @click="filtre = 'retard'">En retard · {{ nombreEnRetard }}</button>
            <button class="seg" :class="{ on: filtre === 'miennes' }" @click="filtre = 'miennes'">Les miennes · {{ nombreMiennes }}</button>
          </div>

          <div v-for="a in listeFiltree" :key="a.id">
            <div class="row" :style="etat(a).tag === 't-red' ? 'border-color:#F5C6C2' : ''" role="button" tabindex="0" @click="basculer(a)" @keydown.enter="basculer(a)">
              <span class="lead" :class="etat(a).lead"><Icone :nom="etat(a).icone" /></span>
              <div class="tx">
                <b>{{ a.libelle }}</b>
                <div class="meta">
                  <span>{{ actions.nomUtilisateur(a.responsable_id) ?? `Utilisateur #${a.responsable_id}` }}</span>
                  <span :style="a.en_retard ? 'color:var(--red);font-weight:650' : ''">
                    {{ a.en_retard ? "En retard" : `Échéance ${formaterDate(a.echeance)}` }}
                  </span>
                </div>
                <div class="trk" style="margin-top: 7px"><div class="fl" :class="etat(a).barre" :style="{ width: a.avancement + '%' }"></div></div>
              </div>
              <span class="tag" :class="etat(a).tag">{{ etat(a).libelle }}</span>
            </div>
            <div v-if="actionEnAction === a.id" class="card" style="padding: 11px; margin: -4px 0 10px">
              <label class="f">Avancement (%)</label>
              <input v-model="nouvelAvancement" type="number" min="0" max="100" class="inp" />
              <div class="btnrow" style="margin-top: 8px">
                <button class="btn pri sm" style="width: auto" @click.stop="enregistrerAvancement(a)">Mettre à jour</button>
                <button v-if="a.statut !== 'cloturee'" class="btn gh sm" style="width: auto" @click.stop="cloturer(a)">Clôturer</button>
              </div>
            </div>
          </div>

          <div v-if="!actions.chargement && !listeFiltree.length" class="empty">
            <div class="ic"><Icone nom="check" taille="lg" /></div>
            <b>Aucune action</b>
          </div>

          <div style="height: 12px"></div>
          <button class="btn pri" @click="formulaireOuvert = true">
            <Icone nom="plus" taille="sm" />Nouvelle action
          </button>

          <Modal v-if="formulaireOuvert" titre="Nouvelle action (à partir d'un risque)" @fermer="formulaireOuvert = false">
            <label class="f">Libellé</label>
            <input v-model="nouvelle.libelle" class="inp" placeholder="Ex. Vérification des installations électriques" />
            <label class="f">Risque d'origine</label>
            <select v-model="nouvelle.risque_id" class="inp">
              <option value="" disabled>Choisir…</option>
              <option v-for="r in actions.risques" :key="r.id" :value="r.id">{{ r.danger }}</option>
            </select>
            <label class="f">Type de mesure</label>
            <select v-model="nouvelle.type_mesure" class="inp">
              <option value="corrective">Corrective</option>
              <option value="preventive">Préventive</option>
              <option value="amelioration">Amélioration</option>
            </select>
            <label class="f">Responsable</label>
            <select v-model="nouvelle.responsable_id" class="inp">
              <option value="" disabled>Choisir…</option>
              <option v-for="u in actions.utilisateurs" :key="u.id" :value="u.id">{{ u.prenom }} {{ u.nom }}</option>
            </select>
            <label class="f">Échéance</label>
            <input v-model="nouvelle.echeance" type="date" class="inp" />
            <div v-if="erreurFormulaire" class="banner err" style="margin-top: 8px">{{ erreurFormulaire }}</div>
            <div class="btnrow" style="margin-top: 10px">
              <button class="btn pri sm" style="width: auto" @click="soumettre">Enregistrer</button>
              <button class="btn gh sm" style="width: auto" @click="formulaireOuvert = false">Annuler</button>
            </div>
          </Modal>

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

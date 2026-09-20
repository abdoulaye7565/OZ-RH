<script setup>
/**
 * Écran de validation d'un permis — maquette #s-permis, "vue responsable"
 * (figure A.6 du CDC). Les 4 lignes de contrôle viennent de
 * `controles.details` (backend, enrichi au prompt 2.3 pour cet écran
 * précisément — voir docs/JOURNAL.md) : chaque condition de la règle centrale
 * (prompt 2.2) est montrée avec son résultat, pas seulement celles en échec.
 *
 * 2026-09-10 (revue d'ensemble) : cet écran appelait l'API directement et
 * affichait « Site #1 » / « Utilisateur #3 ». Il passe par usePermisStore
 * (comme le reste de l'app) et résout les noms via les getters du store —
 * c'est l'écran qui autorise un travail en hauteur, le responsable doit voir
 * qui monte. Ajout aussi du bouton « Refuser » (route /permis/{id}/refuser
 * déjà présente, jamais exposée) : un permis non conforme ne restait sinon
 * ni validé ni refusé.
 */
import { computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import Icone from "../components/Icone.vue";
import Modal from "../components/Modal.vue";
import BandeauReseau from "../components/BandeauReseau.vue";
import { useAuthStore } from "../stores/auth";
import { usePermisStore } from "../stores/permis";

const route = useRoute();
const router = useRouter();
const auth = useAuthStore();
const permisStore = usePermisStore();
// Clôture ajoutée le 2026-09-19 ("tu corriges tout") : POST .../cloturer
// existait côté serveur sans bouton, réservé à VALIDER_PERMIS.
const peutCloturer = computed(() => ["responsable", "administrateur"].includes(auth.utilisateur?.role));

const permis = ref(null);
const chargement = ref(true);
const erreur = ref(null);
const actionEnCours = ref(false);
const refusOuvert = ref(false);
const motifRefus = ref("");

async function charger() {
  chargement.value = true;
  erreur.value = null;
  try {
    permis.value = await permisStore.chargerPourValidation(route.params.id);
  } catch (e) {
    erreur.value = e instanceof Error ? e.message : "Impossible de charger le permis";
  } finally {
    chargement.value = false;
  }
}
onMounted(charger);

const details = computed(() => permis.value?.controles?.details ?? []);
const nombreConformes = computed(() => details.value.filter((d) => d.conforme).length);
const peutValider = computed(() => permis.value?.controles?.conforme === true);

const nomSite = computed(() =>
  permis.value ? (permisStore.nomSite(permis.value.site_id) ?? `Site #${permis.value.site_id}`) : ""
);
const nomsIntervenants = computed(() =>
  (permis.value?.intervenant_ids ?? [])
    .map((id) => permisStore.nomUtilisateur(id) ?? `Utilisateur #${id}`)
    .join(", ")
);
const nomSurveillant = computed(() => {
  if (!permis.value?.surveillant_id) return null;
  return permisStore.nomUtilisateur(permis.value.surveillant_id) ?? `Utilisateur #${permis.value.surveillant_id}`;
});

function formaterHeure(iso) {
  return new Date(iso).toLocaleTimeString("fr-FR", { hour: "2-digit", minute: "2-digit" });
}

async function valider() {
  actionEnCours.value = true;
  erreur.value = null;
  try {
    permis.value = await permisStore.valider(permis.value.id);
  } catch (e) {
    if (e instanceof Error && e.statut === 409) {
      // Le serveur réévalue et peut renvoyer un blocage à jour : on recharge
      // pour refléter l'état réel plutôt que d'afficher un message figé.
      await charger();
    } else {
      erreur.value = e instanceof Error ? e.message : "Action impossible";
    }
  } finally {
    actionEnCours.value = false;
  }
}

async function cloturer() {
  actionEnCours.value = true;
  erreur.value = null;
  try {
    permis.value = await permisStore.cloturer(permis.value.id);
  } catch (e) {
    erreur.value = e instanceof Error ? e.message : "Clôture impossible";
  } finally {
    actionEnCours.value = false;
  }
}

async function confirmerRefus() {
  if (!motifRefus.value.trim()) {
    erreur.value = "Un motif est obligatoire pour refuser un permis.";
    return;
  }
  actionEnCours.value = true;
  erreur.value = null;
  try {
    permis.value = await permisStore.refuser(permis.value.id, motifRefus.value.trim());
    refusOuvert.value = false;
  } catch (e) {
    erreur.value = e instanceof Error ? e.message : "Refus impossible";
  } finally {
    actionEnCours.value = false;
  }
}
</script>

<template>
  <div class="ecran-mobile">
    <BandeauReseau />
    <header class="hd">
      <button class="back" aria-label="Retour" @click="router.back()"><Icone nom="back" /></button>
      <div>
        <h1>Permis {{ permis?.reference ?? "…" }}</h1>
        <div class="sub" v-if="permis">Demande reçue à {{ formaterHeure(permis.cree_le) }}</div>
      </div>
    </header>

    <div class="body">
      <div class="pad">
        <div v-if="chargement" class="skel" style="height: 120px"></div>

        <template v-else-if="permis">
          <div class="card" style="padding: 12px; margin-bottom: 12px">
            <div class="kv"><span>Site</span><b>{{ nomSite }}</b></div>
            <div class="kv"><span>Travaux</span><b>{{ permis.nature_travaux }}</b></div>
            <div class="kv"><span>Intervenants</span><b>{{ nomsIntervenants }}</b></div>
            <div class="kv"><span>Surveillant</span><b>{{ nomSurveillant ?? "Aucun désigné" }}</b></div>
            <div class="kv">
              <span>Créneau</span>
              <b>{{ formaterHeure(permis.debut_validite) }} → {{ formaterHeure(permis.fin_validite) }}</b>
            </div>
          </div>

          <div v-if="permis.evaluations_slam?.length" class="sec">ÉVALUATIONS SLAM RATTACHÉES</div>
          <ul v-if="permis.evaluations_slam?.length" class="cl">
            <li v-for="ev in permis.evaluations_slam" :key="ev.id" :class="ev.decision === 'GO' ? 'ok' : 'ko'">
              <span class="cb"><Icone :nom="ev.decision === 'GO' ? 'check' : 'x'" taille="sm" /></span>
              <span class="tx">
                {{ ev.utilisateur_nom ?? `Utilisateur #${ev.utilisateur_id}` }} — {{ ev.decision.replace('_', ' ') }}
                <span class="sub" style="display: block">
                  {{ new Date(ev.date).toLocaleString("fr-FR", { day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit" }) }}{{ ev.motif ? ` · ${ev.motif}` : "" }}
                </span>
              </span>
            </li>
          </ul>

          <div class="sec">
            CONTRÔLES AUTOMATIQUES <span class="n">{{ nombreConformes }}/{{ details.length }}</span>
          </div>
          <ul class="cl">
            <li v-for="d in details" :key="d.cle" :class="d.conforme ? 'ok' : 'ko'">
              <span class="cb"><Icone :nom="d.conforme ? 'check' : 'x'" taille="sm" /></span>
              <span class="tx">{{ d.libelle }}<span v-if="d.detail"> — {{ d.detail }}</span></span>
            </li>
          </ul>

          <div v-if="!peutValider && permis.statut !== 'delivre' && permis.statut !== 'refuse'" class="banner err">
            <Icone nom="lock" taille="sm" style="margin-top: 1px" />
            <div><b>Validation bloquée.</b> Corrigez les points en rouge ci-dessus, ou refusez la demande avec un motif.</div>
          </div>

          <div v-if="erreur" class="banner err">{{ erreur }}</div>

          <template v-if="permis.statut === 'delivre'">
            <div class="banner info">Ce permis a déjà été délivré.</div>
            <button v-if="peutCloturer" class="btn pri sm" style="width: auto; margin-top: 8px" :disabled="actionEnCours" @click="cloturer">
              Clôturer le permis
            </button>
          </template>
          <template v-else-if="permis.statut === 'cloture'">
            <div class="banner info">Ce permis est clôturé.</div>
          </template>
          <template v-else-if="permis.statut === 'refuse'">
            <div class="banner info">Ce permis a été refusé.</div>
          </template>
          <template v-else>
            <div class="btnrow" style="margin-top: 4px">
              <button class="btn pri sm" style="width: auto" :disabled="!peutValider || actionEnCours" @click="valider">
                <Icone nom="lock" v-if="!peutValider" taille="sm" />
                Valider et délivrer
              </button>
              <button class="btn gh sm" style="width: auto" :disabled="actionEnCours" @click="refusOuvert = true; motifRefus = ''">
                Refuser
              </button>
            </div>
          </template>
        </template>
      </div>
    </div>

    <Modal v-if="refusOuvert" titre="Refuser le permis" @fermer="refusOuvert = false">
      <label class="f">Motif du refus (obligatoire)</label>
      <textarea v-model="motifRefus" class="inp" rows="3" placeholder="Ex. EPI non conforme, surveillant absent…"></textarea>
      <div v-if="erreur" class="banner err" style="margin: 8px 0">{{ erreur }}</div>
      <div class="btnrow" style="margin-top: 10px">
        <button class="btn pri sm" style="width: auto" :disabled="actionEnCours" @click="confirmerRefus">Confirmer le refus</button>
        <button class="btn gh sm" style="width: auto" @click="refusOuvert = false">Annuler</button>
      </div>
    </Modal>
  </div>
</template>

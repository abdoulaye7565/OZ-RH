<script setup>
/**
 * Inspection — fiche de saisie (maquette #s-insp, "Incendie & extincteurs").
 *
 * Deux entrées possibles, gérées par le même écran pour ne pas dupliquer la
 * checklist : une inspection déjà commencée (route /inspections/:id) ou une
 * toute nouvelle (route /inspections/nouvelle?modele=...&site_id=...),
 * arrivant ici sans exister encore côté serveur — `POST /inspections`
 * exige au moins un point coté (InspectionCreation), impossible de créer
 * l'inspection avant la première réponse. Elle est donc créée au premier
 * clic, puis chaque clic suivant renvoie l'état complet des réponses
 * (PATCH /points remplace le tableau entier, ne fusionne pas — service
 * mettre_a_jour_points).
 */
import { computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import Icone from "../components/Icone.vue";
import BandeauReseau from "../components/BandeauReseau.vue";
import { useInspectionsStore } from "../stores/inspections";
import { useAuthStore } from "../stores/auth";
import api from "../services/api";

const route = useRoute();
const router = useRouter();
const inspections = useInspectionsStore();
const auth = useAuthStore();

const estNouvelle = computed(() => route.name === "inspection-nouvelle");
const chargement = ref(true);
const erreur = ref(null);
const enregistrement = ref(false);

// point_checklist_id (number) -> "C" | "NC" | "SO"
const reponses = ref({});
const observations = ref({}); // point_checklist_id -> texte

onMounted(async () => {
  try {
    await inspections.chargerReferentielsSiBesoin();
    if (estNouvelle.value) {
      await inspections.chargerPoints(route.query.modele);
      inspections.inspection = null;
    } else {
      const insp = await inspections.chargerInspection(route.params.id);
      for (const p of insp.points) {
        reponses.value[p.point_checklist_id] = p.cotation;
        if (p.observation) observations.value[p.point_checklist_id] = p.observation;
      }
    }
  } catch (e) {
    erreur.value = e?.message ?? "Impossible de charger l'inspection";
  } finally {
    chargement.value = false;
  }
});

const nombreConformes = computed(() => Object.values(reponses.value).filter((v) => v === "C").length);
const nombreCotes = computed(() => Object.values(reponses.value).filter((v) => v === "C" || v === "NC").length);
const tauxAffiche = computed(() => (nombreCotes.value ? Math.round((nombreConformes.value / nombreCotes.value) * 100) : null));

function construirePoints() {
  return Object.entries(reponses.value).map(([point_checklist_id, cotation]) => ({
    point_checklist_id: Number(point_checklist_id),
    cotation,
    observation: observations.value[point_checklist_id] || null,
  }));
}

async function coter(pointId, valeur) {
  if (inspections.inspection?.statut === "cloturee") return;
  reponses.value[pointId] = valeur;
  enregistrement.value = true;
  erreur.value = null;
  try {
    if (!inspections.inspection) {
      const insp = await inspections.creer({
        modele: route.query.modele,
        site_id: Number(route.query.site_id),
        equipement_id: route.query.equipement_id ? Number(route.query.equipement_id) : null,
        points: construirePoints(),
      });
      // Remplace l'URL "nouvelle" par l'URL réelle : un rechargement de page
      // retombe alors sur l'inspection déjà créée, pas sur un nouveau départ.
      router.replace({ name: "inspection-detail", params: { id: insp.id } });
    } else {
      await inspections.mettreAJourPoints(inspections.inspection.id, construirePoints());
    }
  } catch (e) {
    erreur.value = e?.message ?? "Enregistrement impossible, réessayez";
  } finally {
    enregistrement.value = false;
  }
}

async function deposerPhoto(pointId, fichier) {
  if (!inspections.inspection || !fichier) return;
  const donnees = new FormData();
  donnees.set("photo", fichier);
  try {
    inspections.inspection = await api.requete(`/api/v1/inspections/${inspections.inspection.id}/points/${pointId}/photo`, {
      methode: "POST",
      corps: donnees,
    });
  } catch (e) {
    erreur.value = e?.message ?? "Impossible d'ajouter la photo";
  }
}

async function terminer() {
  if (!inspections.inspection) return;
  enregistrement.value = true;
  erreur.value = null;
  try {
    await inspections.cloturer(inspections.inspection.id);
  } catch (e) {
    erreur.value = e?.message ?? "Impossible de clôturer l'inspection";
  } finally {
    enregistrement.value = false;
  }
}
</script>

<template>
  <div class="ecran-mobile">
    <BandeauReseau />
    <header class="hd">
      <button class="back" aria-label="Retour" @click="router.push({ name: 'inspections' })"><Icone nom="back" /></button>
      <div>
        <h1>{{ inspections.libelleType(estNouvelle ? route.query.modele : inspections.inspection?.modele) }}</h1>
        <div class="sub">
          {{ inspections.nomSite(Number(estNouvelle ? route.query.site_id : inspections.inspection?.site_id)) ?? "" }}
          <template v-if="auth.utilisateur"> · {{ auth.utilisateur.prenom }} {{ auth.utilisateur.nom }}</template>
        </div>
      </div>
    </header>

    <div class="body">
      <div class="pad">
        <div v-if="chargement">Chargement…</div>

        <template v-else>
          <div class="statbar">
            <span>Conformité</span>
            <span class="v" :style="tauxAffiche === null ? 'color:var(--mut)' : ''">{{ tauxAffiche === null ? "—" : `${tauxAffiche} %` }}</span>
          </div>

          <ul class="cl">
            <li v-for="p in inspections.pointsChecklist" :key="p.id">
              <span class="tx">
                {{ p.libelle }}
                <span v-if="reponses[p.id] === 'NC' && inspections.inspection" style="display: block; margin-top: 4px">
                  <input
                    type="file"
                    accept="image/*"
                    capture="environment"
                    style="font-size: 11px"
                    @change="(e) => deposerPhoto(p.id, e.target.files[0])"
                  />
                </span>
              </span>
              <span class="tri">
                <button class="c" :class="{ on: reponses[p.id] === 'C' }" @click="coter(p.id, 'C')">C</button>
                <button class="n" :class="{ on: reponses[p.id] === 'NC' }" @click="coter(p.id, 'NC')">NC</button>
                <button class="s" :class="{ on: reponses[p.id] === 'SO' }" @click="coter(p.id, 'SO')">SO</button>
              </span>
            </li>
          </ul>

          <div class="banner info">
            <Icone nom="check" taille="sm" style="margin-top: 1px" />
            <div>Chaque « NC » crée une action corrective, avec photo possible.</div>
          </div>

          <div v-if="erreur" class="banner err" style="margin-top: 10px">{{ erreur }}</div>

          <template v-if="inspections.inspection?.statut === 'cloturee'">
            <div class="banner info" style="margin-top: 10px">Cette inspection est clôturée.</div>
          </template>
          <button v-else class="btn pri" style="margin-top: 10px" :disabled="!inspections.inspection || enregistrement" @click="terminer">
            Terminer et signer
          </button>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
/**
 * SLAM & permis — vue desktop (maquette #p-hauteur).
 *
 * Écart assumé : "Historique complet" (lien de la maquette) et un formulaire
 * de demande ne sont pas dans le fragment fourni — un bouton "Demander un
 * permis" a été ajouté au-dessus du tableau, seule façon de rendre
 * POST /permis atteignable depuis le desktop (même compromis que côté
 * mobile, voir PermisView.vue). Les métriques réutilisent les données déjà
 * chargées plutôt que d'appeler un indicateur dédié qui n'existe pas côté
 * API.
 */
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import BarrePagination from "../components/BarrePagination.vue";
import Icone from "../components/Icone.vue";
import Modal from "../components/Modal.vue";
import { useRechercheEtPagination } from "../composables/useRechercheEtPagination";
import { usePermisStore } from "../stores/permis";
import { telechargerPdf } from "../utils/telechargement";

const router = useRouter();

const pdfEnCours = ref(null);
async function telechargerPermis(p) {
  pdfEnCours.value = p.id;
  try {
    await telechargerPdf(`/api/v1/permis/${p.id}/export-pdf`, `${p.reference ?? "permis-" + p.id}.pdf`);
  } catch (e) {
    permis.erreur = e?.message ?? "Téléchargement du PDF impossible";
  } finally {
    pdfEnCours.value = null;
  }
}
const permis = usePermisStore();
onMounted(() => permis.charger());

const SUPPORTS = [
  { valeur: "pylone", libelle: "Pylône" },
  { valeur: "toiture", libelle: "Toiture" },
  { valeur: "echelle", libelle: "Échelle" },
  { valeur: "autre", libelle: "Autre" },
];

const STYLE_STATUT = {
  demande: "t-or",
  bloque: "t-red",
  delivre: "t-bl",
  cloture: "t-gr",
  refuse: "t-gy",
};
const LIBELLE_STATUT = { demande: "À valider", bloque: "Bloqué", delivre: "En cours", cloture: "Clôturé", refuse: "Refusé" };

const slamRecentes = computed(() => permis.evaluationsSlam.slice(0, 6));
const nombreNoGo = computed(() => permis.evaluationsSlam.filter((e) => e.decision === "NO_GO").length);

// GET /slam/{id}/export-pdf existait côté serveur sans bouton (2026-09-19,
// "tu corriges tout").
const pdfSlamEnCours = ref(null);
async function telechargerSlam(e) {
  pdfSlamEnCours.value = e.id;
  try {
    await telechargerPdf(`/api/v1/slam/${e.id}/export-pdf`, `slam-${e.id}.pdf`);
  } catch (err) {
    permis.erreur = err?.message ?? "Téléchargement du PDF impossible";
  } finally {
    pdfSlamEnCours.value = null;
  }
}

function correspond(p, terme) {
  return (
    String(p.reference ?? "").toLowerCase().includes(terme) ||
    p.nature_travaux?.toLowerCase().includes(terme) ||
    (permis.nomSite(p.site_id) ?? "").toLowerCase().includes(terme) ||
    (LIBELLE_STATUT[p.statut] ?? "").toLowerCase().includes(terme)
  );
}
const { recherche, page, totalPages, resultats, elementsPage, allerPage } =
  useRechercheEtPagination(computed(() => permis.liste), correspond, 12);

function formaterCreneau(p) {
  const debut = new Date(p.debut_validite);
  const fin = new Date(p.fin_validite);
  return `${debut.toLocaleTimeString("fr-FR", { hour: "2-digit", minute: "2-digit" })}–${fin.toLocaleTimeString("fr-FR", { hour: "2-digit", minute: "2-digit" })}`;
}
function formaterDateHeure(iso) {
  return new Date(iso).toLocaleString("fr-FR", { day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit" });
}

const formulaireOuvert = ref(false);
const vide = () => ({
  site_id: "",
  nature_travaux: "",
  support: "pylone",
  hauteur_estimee: "",
  intervenant_ids: [],
  surveillant_id: "",
  date: new Date().toISOString().slice(0, 10),
  heure_debut: "08:00",
  heure_fin: "12:00",
});
const nouveau = ref(vide());
const erreurFormulaire = ref(null);

function basculerIntervenant(id) {
  const i = nouveau.value.intervenant_ids.indexOf(id);
  if (i === -1) nouveau.value.intervenant_ids.push(id);
  else nouveau.value.intervenant_ids.splice(i, 1);
}

async function soumettre() {
  erreurFormulaire.value = null;
  try {
    await permis.creer({
      site_id: Number(nouveau.value.site_id),
      nature_travaux: nouveau.value.nature_travaux,
      support: nouveau.value.support,
      hauteur_estimee: nouveau.value.hauteur_estimee ? Number(nouveau.value.hauteur_estimee) : null,
      intervenant_ids: nouveau.value.intervenant_ids,
      surveillant_id: nouveau.value.surveillant_id ? Number(nouveau.value.surveillant_id) : null,
      debut_validite: `${nouveau.value.date}T${nouveau.value.heure_debut}:00`,
      fin_validite: `${nouveau.value.date}T${nouveau.value.heure_fin}:00`,
    });
    formulaireOuvert.value = false;
    nouveau.value = vide();
  } catch (e) {
    erreurFormulaire.value = e?.message ?? "Impossible d'enregistrer cette demande de permis";
  }
}
</script>

<template>
  <div>
    <div v-if="permis.erreur" class="banner err">{{ permis.erreur }}</div>

    <div class="mets" style="grid-template-columns: repeat(4, 1fr)">
      <div class="met">
        <div class="hd"><span class="ic m-bl"><Icone nom="climb" taille="sm" /></span>Permis en cours</div>
        <div class="v">{{ permis.permisActifs.length }}</div>
        <div class="t flat">tous sites confondus</div>
      </div>
      <div class="met">
        <div class="hd"><span class="ic m-or"><Icone nom="clock" taille="sm" /></span>En attente de validation</div>
        <div class="v">{{ permis.enAttente.length }}</div>
        <div class="t down">demande ou blocage</div>
      </div>
      <div class="met">
        <div class="hd"><span class="ic m-gr"><Icone nom="check" taille="sm" /></span>SLAM enregistrés</div>
        <div class="v">{{ permis.evaluationsSlam.length }}</div>
        <div class="t up">toutes décisions</div>
      </div>
      <div class="met">
        <div class="hd"><span class="ic m-gd"><Icone nom="alert" taille="sm" /></span>NO GO déclarés</div>
        <div class="v">{{ nombreNoGo }}</div>
        <div class="t up">interventions évitées</div>
      </div>
    </div>

    <Modal v-if="formulaireOuvert" titre="Demander un permis" @fermer="formulaireOuvert = false">
      <div class="grid2">
        <div>
          <label class="f">Site</label>
          <select v-model="nouveau.site_id" class="inp">
            <option value="" disabled>Choisir…</option>
            <option v-for="s in permis.sites" :key="s.id" :value="s.id">{{ s.nom }}</option>
          </select>
          <label class="f">Nature des travaux</label>
          <input v-model="nouveau.nature_travaux" class="inp" placeholder="Ex. Pose LiteBeam 5AC" />
          <label class="f">Support</label>
          <select v-model="nouveau.support" class="inp">
            <option v-for="s in SUPPORTS" :key="s.valeur" :value="s.valeur">{{ s.libelle }}</option>
          </select>
          <label class="f">Hauteur estimée (m, facultatif)</label>
          <input v-model="nouveau.hauteur_estimee" type="number" min="0" step="0.5" class="inp" />
        </div>
        <div>
          <label class="f">Date</label>
          <input v-model="nouveau.date" type="date" class="inp" />
          <div class="grid2">
            <div>
              <label class="f">Début</label>
              <input v-model="nouveau.heure_debut" type="time" class="inp" />
            </div>
            <div>
              <label class="f">Fin</label>
              <input v-model="nouveau.heure_fin" type="time" class="inp" />
            </div>
          </div>
          <label class="f">Surveillant (facultatif)</label>
          <select v-model="nouveau.surveillant_id" class="inp">
            <option value="">Aucun</option>
            <option v-for="u in permis.utilisateurs" :key="u.id" :value="u.id">{{ u.prenom }} {{ u.nom }}</option>
          </select>
          <label class="f">Intervenants</label>
          <div style="max-height: 110px; overflow-y: auto; border: 1px solid var(--line); border-radius: 8px; padding: 6px 8px">
            <div v-for="u in permis.utilisateurs" :key="u.id" style="font-size: 12.5px; padding: 3px 0">
              <label style="display: flex; align-items: center; gap: 6px">
                <input type="checkbox" :checked="nouveau.intervenant_ids.includes(u.id)" @change="basculerIntervenant(u.id)" />
                {{ u.prenom }} {{ u.nom }}
              </label>
            </div>
          </div>
        </div>
      </div>
      <div v-if="erreurFormulaire" class="banner err" style="margin-top: 8px">{{ erreurFormulaire }}</div>
      <div style="display: flex; gap: 8px; margin-top: 10px">
        <button class="btn pri" style="width: auto" @click="soumettre">Envoyer la demande</button>
        <button class="btn gh" style="width: auto" @click="formulaireOuvert = false">Annuler</button>
      </div>
    </Modal>

    <div class="grid2">
      <div class="card">
        <div class="ch">
          <Icone nom="clip" style="color: var(--navy2)" /><h3>Permis de travail en hauteur</h3>
          <span style="flex: 1"></span>
          <div class="srch">
            <Icone nom="search" taille="sm" />
            <input v-model="recherche" placeholder="Rechercher un permis, un site…" />
          </div>
          <span
            class="r"
            style="cursor: pointer"
            role="button"
            tabindex="0"
            @click="formulaireOuvert = true"
            @keydown.enter="formulaireOuvert = true"
          >Demander un permis</span>
        </div>
        <table>
          <thead><tr><th>N°</th><th>Site</th><th>Créneau</th><th>Statut</th><th></th></tr></thead>
          <tbody>
            <tr
              v-for="p in elementsPage"
              :key="p.id"
              style="cursor: pointer"
              @click="router.push({ name: 'permis-validation', params: { id: p.id } })"
            >
              <td><b>{{ p.reference ?? `#${p.id}` }}</b></td>
              <td>{{ permis.nomSite(p.site_id) ?? `Site #${p.site_id}` }}<div class="sub">{{ p.nature_travaux }}</div></td>
              <td>{{ formaterCreneau(p) }}</td>
              <td><span class="tag" :class="STYLE_STATUT[p.statut] ?? 't-gy'">{{ LIBELLE_STATUT[p.statut] ?? p.statut }}</span></td>
              <td style="text-align: right">
                <button class="btn gh sm" style="width: auto" :disabled="pdfEnCours === p.id" @click.stop="telechargerPermis(p)">
                  <Icone nom="dl" taille="sm" />PDF
                </button>
              </td>
            </tr>
            <tr v-if="!permis.chargement && !permis.liste.length"><td colspan="5" style="color: var(--mut)">Aucun permis.</td></tr>
            <tr v-if="permis.liste.length && !resultats.length"><td colspan="5" style="color: var(--mut)">Aucun permis ne correspond à la recherche.</td></tr>
          </tbody>
        </table>
        <BarrePagination :page="page" :total-pages="totalPages" @changer="allerPage">
          {{ resultats.length }} sur {{ permis.liste.length }} permis
        </BarrePagination>
      </div>
      <div class="card">
        <div class="ch"><Icone nom="climb" style="color: var(--gold)" /><h3>Décisions SLAM récentes</h3></div>
        <table>
          <tbody>
            <tr v-for="e in slamRecentes" :key="e.id">
              <td>
                <div class="cellrow">
                  <span class="mini" :class="e.decision === 'GO' ? 'm-gr' : 'm-red'"><Icone :nom="e.decision === 'GO' ? 'check' : 'x'" taille="sm" /></span>
                  <div>
                    <b>{{ e.decision }} — {{ permis.nomUtilisateur(e.utilisateur_id) ?? `Utilisateur #${e.utilisateur_id}` }}</b>
                    <div class="sub">{{ formaterDateHeure(e.date) }}{{ e.motif ? ` · ${e.motif}` : "" }}</div>
                  </div>
                </div>
              </td>
              <td style="text-align: right; white-space: nowrap">
                <span class="tag" :class="e.decision === 'GO' ? 't-gr' : 't-red'">{{ e.decision.replace('_', ' ') }}</span>
                <button class="btn gh sm" style="width: auto; margin-left: 6px" :disabled="pdfSlamEnCours === e.id" aria-label="Télécharger le PDF" @click="telechargerSlam(e)">
                  <Icone nom="dl" taille="sm" />
                </button>
              </td>
            </tr>
            <tr v-if="!slamRecentes.length"><td style="color: var(--mut)">Aucune évaluation SLAM.</td></tr>
          </tbody>
        </table>
        <div class="cb" style="padding-top: 0">
          <div class="banner info" style="margin: 0">
            <Icone nom="shield" taille="sm" style="margin-top: 1px" />
            <div>Un NO GO n'est jamais une faute : chacun est analysé et alimente le registre des risques.</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

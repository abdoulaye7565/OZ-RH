<script setup>
/**
 * Permis de travail en hauteur — vue mobile.
 *
 * Écart assumé : ni la maquette mobile ni la desktop n'ont d'écran dédié à
 * une "liste" ou une "demande" de permis en tant que telles — seul
 * `#s-permis` existe, et c'est la vue responsable de validation (déjà
 * construite, PermisValidationView.vue). Le point d'entrée réel de la
 * maquette est le tuile "SLAM & permis" du menu, qui ne mène qu'au stepper
 * SLAM. Sans un écran de demande, `POST /permis` (avec sa vraie règle de
 * blocage — EPI, SLAM GO, surveillant) resterait inaccessible depuis le
 * mobile : construit ici en suivant le langage visuel des autres écrans
 * (métriques + liste + formulaire repliable, comme Risques/Actions),
 * plutôt qu'inventé sans référence.
 */
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import Icone from "../components/Icone.vue";
import Modal from "../components/Modal.vue";
import BandeauReseau from "../components/BandeauReseau.vue";
import { usePermisStore } from "../stores/permis";

const router = useRouter();
const permis = usePermisStore();
onMounted(() => permis.chargerPourDemande());

const SUPPORTS = [
  { valeur: "pylone", libelle: "Pylône" },
  { valeur: "toiture", libelle: "Toiture" },
  { valeur: "echelle", libelle: "Échelle" },
  { valeur: "autre", libelle: "Autre" },
];

const STYLE_STATUT = {
  demande: { tag: "t-or", libelle: "À VALIDER" },
  bloque: { tag: "t-red", libelle: "BLOQUÉ" },
  delivre: { tag: "t-bl", libelle: "EN COURS" },
  cloture: { tag: "t-gr", libelle: "CLÔTURÉ" },
  refuse: { tag: "t-gy", libelle: "REFUSÉ" },
};

function formaterCreneau(p) {
  const debut = new Date(p.debut_validite);
  const fin = new Date(p.fin_validite);
  return `${debut.toLocaleDateString("fr-FR")} · ${debut.toLocaleTimeString("fr-FR", { hour: "2-digit", minute: "2-digit" })} → ${fin.toLocaleTimeString("fr-FR", { hour: "2-digit", minute: "2-digit" })}`;
}

function ouvrirPermis(p) {
  router.push({ name: "permis-validation", params: { id: p.id } });
}

// --- Formulaire de demande ---
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
  <div class="ecran-mobile">
    <BandeauReseau />
    <header class="hd">
      <button class="back" aria-label="Retour" @click="router.push({ name: 'menu' })"><Icone nom="back" /></button>
      <div>
        <h1>Permis de travail</h1>
        <div class="sub">{{ permis.permisActifs.length }} en cours · {{ permis.enAttente.length }} en attente</div>
      </div>
    </header>

    <div class="wrap">
      <div class="body">
        <div class="pad">
          <div v-if="permis.erreur" class="banner err">{{ permis.erreur }}</div>
          <div v-else-if="permis.chargement" class="skel" style="height: 64px"></div>

          <div
            v-for="p in permis.liste"
            :key="p.id"
            class="row"
            role="button"
            tabindex="0"
            @click="ouvrirPermis(p)"
            @keydown.enter="ouvrirPermis(p)"
          >
            <span class="lead" :class="STYLE_STATUT[p.statut]?.tag === 't-red' ? 'red' : 'nv'"><Icone nom="climb" /></span>
            <div class="tx">
              <b>{{ p.reference ?? `Permis #${p.id}` }} — {{ p.nature_travaux }}</b>
              <div class="meta">
                <span>{{ permis.nomSite(p.site_id) ?? `Site #${p.site_id}` }}</span>
                <span>{{ formaterCreneau(p) }}</span>
              </div>
            </div>
            <span class="tag" :class="STYLE_STATUT[p.statut]?.tag ?? 't-gy'">{{ STYLE_STATUT[p.statut]?.libelle ?? p.statut }}</span>
          </div>

          <div v-if="!permis.chargement && !permis.liste.length" class="empty">
            <div class="ic"><Icone nom="climb" taille="lg" /></div>
            <b>Aucun permis</b>
          </div>

          <div style="height: 12px"></div>
          <button class="btn pri" @click="formulaireOuvert = true">
            <Icone nom="plus" taille="sm" />Demander un permis
          </button>

          <Modal v-if="formulaireOuvert" titre="Demander un permis" @fermer="formulaireOuvert = false">
            <label class="f">Site</label>
            <select v-model="nouveau.site_id" class="inp">
              <option value="" disabled>Sélectionner…</option>
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
            <label class="f">Intervenants</label>
            <div v-for="u in permis.utilisateurs" :key="u.id" style="font-size: 12.5px; padding: 3px 0">
              <label style="display: flex; align-items: center; gap: 6px">
                <input type="checkbox" :checked="nouveau.intervenant_ids.includes(u.id)" @change="basculerIntervenant(u.id)" />
                {{ u.prenom }} {{ u.nom }}
              </label>
            </div>
            <label class="f">Surveillant (facultatif)</label>
            <select v-model="nouveau.surveillant_id" class="inp">
              <option value="">Aucun</option>
              <option v-for="u in permis.utilisateurs" :key="u.id" :value="u.id">{{ u.prenom }} {{ u.nom }}</option>
            </select>
            <div v-if="erreurFormulaire" class="banner err" style="margin: 8px 0">{{ erreurFormulaire }}</div>
            <div class="btnrow" style="margin-top: 8px">
              <button class="btn pri sm" style="width: auto" @click="soumettre">Envoyer la demande</button>
              <button class="btn gh sm" style="width: auto" @click="formulaireOuvert = false">Annuler</button>
            </div>
          </Modal>

          <div class="banner info" style="margin-top: 11px">
            <Icone nom="lock" taille="sm" style="margin-top: 1px" />
            <div>Le permis n'est délivré qu'après validation : EPI conformes, SLAM GO de chaque intervenant, et un surveillant désigné.</div>
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
      <button class="tb" @click="router.push({ name: 'assistant-documentaire' })"><Icone nom="chat" />Assistant</button>
      <button class="tb" @click="router.push({ name: 'menu' })"><Icone nom="grid" />Menu</button>
    </nav>
  </div>
</template>

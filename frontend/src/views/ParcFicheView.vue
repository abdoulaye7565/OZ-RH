<script setup>
/**
 * Fiche équipement + nouvelle fiche de configuration — vue mobile (maquette
 * #s-config, "CONFIG MIKROTIK").
 *
 * Écart assumé : maquette et backend en un seul écran plutôt que deux (liste
 * → config directement dans la maquette) — la fiche réelle (configurations,
 * inspections, incidents déjà liés à l'équipement, via GET .../fiche) est
 * plus riche que la maquette et mérite son propre écran. Formulaire de
 * nouvelle configuration limité à MikroTik pour l'instant (seule marque
 * détaillée dans la maquette de référence) ; les 3 autres marques ont une
 * API fonctionnelle (app/schemas/configuration.py) mais pas encore de
 * formulaire dédié ici.
 */
import { onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import Icone from "../components/Icone.vue";
import BandeauReseau from "../components/BandeauReseau.vue";
import { useParcStore } from "../stores/parc";
import { formaterDateCivile } from "../utils/dates";

const route = useRoute();
const router = useRouter();
const parc = useParcStore();
const equipementId = Number(route.params.id);

onMounted(() => parc.chargerFiche(equipementId));

const TYPES_INTERVENTION = ["installation", "reconfiguration", "mise_a_jour", "depannage", "alignement"];

const config = ref({
  type_intervention: "reconfiguration",
  version_logicielle: "",
  adresse_ip_masque: "",
  passerelle: "",
  dhcp_serveur: "",
  mode: "station",
  frequence: "",
  protocole: "",
  signal_dbm: "",
  ccq_pourcent: "",
});
const erreur = ref(null);
const formulaireOuvert = ref(false);

async function soumettre() {
  erreur.value = null;
  try {
    await parc.creerConfiguration(equipementId, {
      type_intervention: config.value.type_intervention,
      version_logicielle: config.value.version_logicielle,
      parametres_reseau: JSON.stringify({
        adresse_ip_masque: config.value.adresse_ip_masque || null,
        passerelle: config.value.passerelle || null,
        dhcp_serveur: config.value.dhcp_serveur || null,
      }),
      parametres_sansfil: JSON.stringify({
        mode: config.value.mode,
        frequence: config.value.frequence,
        protocole: config.value.protocole || null,
      }),
      signal_dbm: config.value.signal_dbm,
      ccq_pourcent: config.value.ccq_pourcent,
    });
    formulaireOuvert.value = false;
  } catch (e) {
    erreur.value = e?.message ?? "Impossible d'enregistrer la fiche";
  }
}
</script>

<template>
  <div class="ecran-mobile">
    <BandeauReseau />
    <header class="hd">
      <button class="back" aria-label="Retour" @click="router.push({ name: 'parc' })"><Icone nom="back" /></button>
      <div v-if="parc.fiche">
        <h1>{{ parc.fiche.equipement.identity }}</h1>
        <div class="sub">{{ parc.fiche.equipement.marque }} {{ parc.fiche.equipement.modele }}</div>
      </div>
    </header>

    <div class="wrap">
      <div class="body">
        <div class="pad">
          <div v-if="parc.erreur" class="banner err">{{ parc.erreur }}</div>

          <template v-if="parc.fiche">
            <div class="kv"><span>N° de série</span><b>{{ parc.fiche.equipement.numero_serie }}</b></div>
            <div class="kv"><span>Emplacement</span><b>{{ parc.fiche.equipement.emplacement }}</b></div>
            <div class="kv"><span>Installé le</span><b>{{ formaterDateCivile(parc.fiche.equipement.date_installation) }}</b></div>
            <div class="kv"><span>Statut</span><b>{{ parc.fiche.equipement.statut }}</b></div>

            <div class="sec" style="margin-top: 16px">HISTORIQUE DES CONFIGURATIONS</div>
            <div v-for="c in parc.fiche.configurations" :key="c.id" class="row">
              <span class="lead nv"><Icone nom="antenna" /></span>
              <div class="tx">
                <b>{{ c.reference }}</b>
                <div class="meta"><span>{{ c.type_intervention }}</span><span>{{ new Date(c.date_intervention).toLocaleDateString("fr-FR") }}</span></div>
              </div>
            </div>
            <p v-if="!parc.fiche.configurations.length" style="font-size: 12px; color: var(--mut)">Aucune fiche de configuration.</p>

            <div v-if="parc.fiche.inspections.length" class="sec" style="margin-top: 16px">INSPECTIONS LIÉES</div>
            <div v-for="i in parc.fiche.inspections" :key="i.id" class="row">
              <span class="lead gr"><Icone nom="clip" /></span>
              <div class="tx"><b>{{ i.statut }}</b><div class="meta"><span>{{ formaterDateCivile(i.date) }}</span><span v-if="i.taux_conformite !== null">{{ Math.round(i.taux_conformite * 100) }} % conforme</span></div></div>
            </div>

            <div v-if="parc.fiche.incidents.length" class="sec" style="margin-top: 16px">INCIDENTS LIÉS</div>
            <div v-for="s in parc.fiche.incidents" :key="s.id" class="row" style="border-color: #f5c6c2">
              <span class="lead red"><Icone nom="alert" /></span>
              <div class="tx"><b>{{ s.reference ?? "en attente" }}</b><div class="meta"><span>{{ s.description.slice(0, 60) }}</span></div></div>
            </div>

            <div v-if="!formulaireOuvert" style="height: 12px"></div>
            <button v-if="!formulaireOuvert && parc.fiche.equipement.marque === 'MikroTik'" class="btn pri" @click="formulaireOuvert = true">
              <Icone nom="plus" taille="sm" />Nouvelle configuration
            </button>
            <p v-else-if="!formulaireOuvert" style="font-size: 11.5px; color: var(--mut)">
              Formulaire de configuration disponible pour MikroTik uniquement pour l'instant.
            </p>

            <div v-if="formulaireOuvert" class="card" style="padding: 13px; margin-top: 4px">
              <div class="sec" style="margin-bottom: 8px">FICHE DE CONFIGURATION — MIKROTIK</div>
              <label class="f">Type d'intervention</label>
              <select v-model="config.type_intervention" class="inp">
                <option v-for="t in TYPES_INTERVENTION" :key="t" :value="t">{{ t }}</option>
              </select>
              <label class="f">Version logicielle</label>
              <input v-model="config.version_logicielle" class="inp" placeholder="Ex. RouterOS 7.15" />
              <label class="f">Réseau — IP / masque</label>
              <input v-model="config.adresse_ip_masque" class="inp" placeholder="10.0.0.2/30" />
              <div style="display: flex; gap: 7px">
                <div style="flex: 1"><input v-model="config.frequence" class="inp" placeholder="Fréquence (5180 MHz)" /></div>
                <div style="flex: 1; max-width: 110px"><input v-model="config.protocole" class="inp" placeholder="nv2" /></div>
              </div>
              <div style="display: flex; gap: 7px; margin-top: 7px">
                <div style="flex: 1"><input v-model="config.signal_dbm" class="inp" placeholder="Signal (dBm)" /></div>
                <div style="flex: 1"><input v-model="config.ccq_pourcent" class="inp" placeholder="CCQ (%)" /></div>
              </div>
              <div class="banner info" style="margin-top: 12px">
                <Icone nom="lock" taille="sm" style="margin-top: 1px" />
                <div>Aucun champ mot de passe ici, par conception : les identifiants vont au coffre-fort.</div>
              </div>
              <div v-if="erreur" class="banner err" style="margin-top: 8px">{{ erreur }}</div>
              <div class="btnrow" style="margin-top: 10px">
                <button class="btn gold sm" style="width: auto" @click="soumettre">Enregistrer la fiche</button>
                <button class="btn gh sm" style="width: auto" @click="formulaireOuvert = false">Annuler</button>
              </div>
            </div>
          </template>

          <div style="height: 56px"></div>
        </div>
      </div>
    </div>
  </div>
</template>

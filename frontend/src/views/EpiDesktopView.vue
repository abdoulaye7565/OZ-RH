<script setup>
/**
 * EPI antichute — vue desktop (maquette #p-epi).
 *
 * Écart assumé : pas de pagination (aucune classe .pagin encore portée dans
 * style.css, et le volume réel — quelques dizaines d'EPI au plus — ne la
 * justifie pas pour l'instant).
 */
import { computed, onMounted } from "vue";
import Icone from "../components/Icone.vue";
import { useEpiStore } from "../stores/epi";
import { formaterDateCivile, joursRestantsCivil } from "../utils/dates";

const epi = useEpiStore();

onMounted(() => epi.charger());

const LIBELLES_TYPE = {
  harnais: "Harnais complet",
  longe: "Longe",
  antichute_mobile: "Antichute mobile",
  casque: "Casque",
  connecteur: "Connecteur",
  ligne_de_vie: "Ligne de vie",
};

const enService = computed(() => epi.liste.filter((e) => e.statut === "en_service").length);
const dues = computed(() => epi.liste.filter((e) => joursRestants(e.prochaine_verification) !== null && joursRestants(e.prochaine_verification) <= 7 && e.statut !== "reforme" && e.statut !== "retire"));
const reformes = computed(() => epi.liste.filter((e) => e.statut === "reforme").length);
const bloquants = computed(() => epi.liste.filter((e) => joursRestants(e.prochaine_verification) !== null && joursRestants(e.prochaine_verification) < 0));

const joursRestants = joursRestantsCivil;
const formaterDate = formaterDateCivile;

function statutTag(item) {
  if (item.statut === "reforme") return { classe: "t-gy", libelle: `Réformé${item.motif_reforme ? " — " + item.motif_reforme.slice(0, 30) : ""}` };
  if (item.statut === "retire") return { classe: "t-gy", libelle: "Retiré" };
  const jours = joursRestants(item.prochaine_verification);
  if (jours !== null && jours < 0) return { classe: "t-red", libelle: "À vérifier" };
  if (jours !== null && jours <= 7) return { classe: "t-or", libelle: `J−${jours}` };
  return { classe: "t-gr", libelle: "En service" };
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

    <div class="card">
      <table>
        <thead>
          <tr>
            <th>N°</th><th>Type</th><th>Marque / modèle</th><th>Affecté à</th><th>Mise en service</th>
            <th>Dernière vérif.</th><th>Prochaine</th><th>Fin de vie</th><th>Statut</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in epi.liste" :key="item.id">
            <td><b>{{ item.numero }}</b></td>
            <td>{{ LIBELLES_TYPE[item.type] ?? item.type }}</td>
            <td>{{ item.marque_modele }}</td>
            <td>{{ item.porteur_id ? epi.nomUtilisateur(item.porteur_id) ?? `Utilisateur #${item.porteur_id}` : "—" }}</td>
            <td>{{ formaterDate(item.date_mise_service) }}</td>
            <td>{{ formaterDate(item.derniere_verification) }}</td>
            <td :style="statutTag(item).classe === 't-red' ? 'color:var(--red);font-weight:650' : statutTag(item).classe === 't-or' ? 'color:var(--orange);font-weight:650' : ''">
              {{ formaterDate(item.prochaine_verification) }}
            </td>
            <td>{{ formaterDate(item.date_limite) }}</td>
            <td><span class="tag" :class="statutTag(item).classe">{{ statutTag(item).libelle }}</span></td>
          </tr>
          <tr v-if="!epi.chargement && !epi.liste.length"><td colspan="9" style="color: var(--mut)">Aucun EPI enregistré.</td></tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

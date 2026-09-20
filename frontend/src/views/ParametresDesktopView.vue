<script setup>
/**
 * Paramètres — vue desktop (maquette #p-param).
 *
 * Ajouté le 2026-09-10 (retour direct de l'utilisateur — "le système
 * n'affiche pas tous les modules dans la barre latérale") : sur les 19
 * écrans desktop de la maquette, un seul n'avait jamais été construit —
 * celui-ci. C'est le module manquant.
 *
 * Écart assumé, délibéré : la maquette montre des liens "Modifier" sur les
 * référentiels et les seuils métier. Ces seuils (criticité 4/8/15,
 * vérification EPI 12 mois...) sont des RÈGLES appliquées côté serveur
 * (CLAUDE.md règle 6, jamais seulement côté interface — règle 7) : les
 * rendre modifiables changerait des règles de sécurité, ce qui se décide
 * explicitement, ne se glisse pas dans cet écran. Cette vue est donc en
 * LECTURE SEULE — comptages réels des référentiels, état réel de la
 * sauvegarde automatique (backend GET /api/v1/parametres) — sans bouton
 * "Modifier" qui ne ferait rien.
 */
import { computed, onMounted, ref } from "vue";
import Icone from "../components/Icone.vue";
import api from "../services/api";

const parametres = ref(null);
const chargement = ref(true);
const erreur = ref(null);

onMounted(async () => {
  try {
    parametres.value = await api.requete("/api/v1/parametres");
  } catch (e) {
    erreur.value = e?.message ?? "Impossible de charger les paramètres";
  } finally {
    chargement.value = false;
  }
});

function formaterDateHeure(iso) {
  if (!iso) return null;
  return new Date(iso).toLocaleString("fr-FR", { day: "2-digit", month: "2-digit", year: "numeric", hour: "2-digit", minute: "2-digit" });
}

const derniereSauvegarde = computed(() => parametres.value?.sauvegarde?.derniere ?? null);

// Règles métier réelles (CLAUDE.md §7.6, code des services concernés) —
// présentées ici comme référence documentaire, pas comme des champs
// modifiables : voir la note d'écart ci-dessus.
const SEUILS = [
  { libelle: "Criticité : seuil « élevé »", valeur: "C ≥ 8" },
  { libelle: "Criticité : seuil « critique »", valeur: "C ≥ 15" },
  { libelle: "Taux de conformité d'une inspection", valeur: "conformes ÷ (conformes + non conformes), « sans objet » exclus" },
  { libelle: "Prochaine vérification EPI", valeur: "dernière vérification + 12 mois" },
  { libelle: "Point non conforme", valeur: "génère automatiquement une action corrective" },
];

const NOTIFICATIONS = [
  { evenement: "Nouveau signalement", destinataires: "Référent SHEQ", delai: "Immédiat" },
  { evenement: "Action arrivant à échéance", destinataires: "Responsable de l'action", delai: "J−7, J, retard" },
  { evenement: "Vérification EPI due", destinataires: "Référent SHEQ · porteur", delai: "J−30, J−7" },
  { evenement: "Permis en attente de validation", destinataires: "Responsable", delai: "Immédiat" },
  { evenement: "Note de satisfaction ≤ 2", destinataires: "Référent SHEQ", delai: "Immédiat" },
];
</script>

<template>
  <div>
    <div v-if="erreur" class="banner err">{{ erreur }}</div>
    <div v-if="chargement" class="skel" style="height: 200px"></div>

    <template v-if="parametres">
      <div class="banner info" style="margin-bottom: 14px">
        <Icone nom="cog" taille="sm" style="margin-top: 1px" />
        <div>
          Écran en lecture seule : les seuils métier ci-dessous sont des règles appliquées côté serveur, pas des
          réglages. Les modifier est un changement de portée qui se décide explicitement.
        </div>
      </div>

      <div class="grid2" style="grid-template-columns: 1fr 1fr">
        <div class="card">
          <div class="ch"><Icone nom="cog" style="color: var(--navy2)" /><h3>Référentiels</h3></div>
          <div class="cb detail">
            <div class="kv"><span>Sites</span><b>{{ parametres.referentiels.sites }} enregistré{{ parametres.referentiels.sites > 1 ? "s" : "" }}</b></div>
            <div class="kv"><span>Équipements du parc</span><b>{{ parametres.referentiels.equipements }}</b></div>
            <div class="kv"><span>Catégories de risques</span><b>{{ parametres.referentiels.categories_risque_utilisees }} utilisées sur {{ parametres.referentiels.categories_risque_total }}</b></div>
            <div class="kv"><span>Types de déchets suivis</span><b>{{ parametres.referentiels.types_dechets }}</b></div>
            <div class="kv"><span>Modèles de checklists d'inspection</span><b>{{ parametres.referentiels.modeles_checklist }}</b></div>
            <div class="kv"><span>Compétences de formation</span><b>{{ parametres.referentiels.competences_formation }}</b></div>
          </div>
        </div>

        <div class="card">
          <div class="ch"><Icone nom="target" style="color: var(--navy2)" /><h3>Seuils et règles métier</h3></div>
          <div class="cb detail">
            <div v-for="s in SEUILS" :key="s.libelle" class="kv">
              <span>{{ s.libelle }}</span><b>{{ s.valeur }}</b>
            </div>
          </div>
        </div>
      </div>

      <div class="grid2" style="grid-template-columns: 1fr 1fr">
        <div class="card">
          <div class="ch"><Icone nom="bell" style="color: var(--navy2)" /><h3>Notifications</h3></div>
          <table>
            <thead><tr><th>Événement</th><th>Destinataires</th><th>Délai</th></tr></thead>
            <tbody>
              <tr v-for="n in NOTIFICATIONS" :key="n.evenement">
                <td>{{ n.evenement }}</td>
                <td>{{ n.destinataires }}</td>
                <td>{{ n.delai }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="card">
          <div class="ch"><Icone nom="shield" style="color: var(--navy2)" /><h3>Sécurité et sauvegarde</h3></div>
          <div class="cb detail">
            <div class="kv">
              <span>Sauvegarde automatique de la base</span>
              <b :style="parametres.sauvegarde.active ? '' : 'color:var(--red)'">
                {{ parametres.sauvegarde.active ? `Active · quotidienne ${String(parametres.sauvegarde.heure).padStart(2, "0")}:00` : "Désactivée" }}
              </b>
            </div>
            <div class="kv">
              <span>Dernière sauvegarde</span>
              <b v-if="derniereSauvegarde" style="color: var(--green)">{{ formaterDateHeure(derniereSauvegarde.horodatage_utc) }} · {{ derniereSauvegarde.type_base }}</b>
              <b v-else style="color: var(--orange)">Aucune sauvegarde encore créée</b>
            </div>
            <div class="kv"><span>Archives conservées</span><b>{{ parametres.sauvegarde.nombre_archives }} (rétention {{ parametres.sauvegarde.retention }})</b></div>
            <div class="kv"><span>Chiffrement du coffre-fort</span><b>Actif · clé maîtresse hors base</b></div>
            <div class="kv"><span>Rétention du journal d'audit</span><b>Illimitée (non modifiable)</b></div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
/**
 * Utilisateurs & rôles — vue desktop (maquette #p-users).
 *
 * Écran réservé à l'administrateur (seul rôle habilité par
 * `Permissions.GERER_UTILISATEURS`) — aucun équivalent mobile, cohérent avec
 * le reste de l'app (l'administration est un usage desktop, CDC 11.1).
 *
 * Écarts assumés :
 * 1. Colonne "Appareil" de la maquette (Web / Mobile / Web · mobile) omise :
 *    rien côté backend ne trace par quel client un compte se connecte —
 *    l'inventer aurait affiché une donnée fictive comme si elle était réelle.
 * 2. "Matrice des droits par rôle" : la maquette montre une grille fine par
 *    module (illustrative, pas lue depuis `core/permissions.py`, qui n'est
 *    exposé par aucune route). Remplacée par le tableau réel et déjà
 *    disponible de CLAUDE.md (section 6, "Rôles et droits") — moins
 *    granulaire mais fidèle à une source de vérité existante plutôt qu'à un
 *    exemple.
 * 3. Nouvelle route backend utilisée : `POST /auth/utilisateurs/{id}
 *    /desactiver` et `.../activer` (ajoutées pour cet écran — aucune route
 *    de modification n'existait, seule la création, voir docs/JOURNAL.md).
 */
import { computed, onMounted, ref } from "vue";
import Icone from "../components/Icone.vue";
import { useUtilisateursStore } from "../stores/utilisateurs";

const utilisateurs = useUtilisateursStore();
onMounted(() => utilisateurs.charger());

const ROLES = [
  { valeur: "administrateur", libelle: "Administrateur", tag: "t-red" },
  { valeur: "referent_sheq", libelle: "Référent SHEQ", tag: "t-or" },
  { valeur: "responsable", libelle: "Responsable", tag: "t-gd" },
  { valeur: "technicien", libelle: "Technicien", tag: "t-bl" },
  { valeur: "collaborateur", libelle: "Collaborateur", tag: "t-gy" },
];
function roleInfo(valeur) {
  return ROLES.find((r) => r.valeur === valeur) ?? { libelle: valeur, tag: "t-gy" };
}

const MATRICE = [
  { role: "Administrateur", perimetre: "Tout, y compris utilisateurs et paramètres" },
  { role: "Référent SHEQ", perimetre: "Risques, actions, inspections, formations, documents — aucun accès au coffre-fort" },
  { role: "Responsable", perimetre: "Valide les permis, consulte les registres, accède au coffre-fort" },
  { role: "Technicien", perimetre: "Signalements, SLAM, configurations, inspections, vérifications EPI ; coffre-fort limité" },
  { role: "Collaborateur", perimetre: "Signalements, consultation de la politique, quiz" },
];

const filtre = ref("actifs"); // "actifs" | "desactives"
const filtreRole = ref("Tous");
const listeFiltree = computed(() => {
  const base = filtre.value === "actifs" ? utilisateurs.actifs : utilisateurs.desactives;
  return filtreRole.value === "Tous" ? base : base.filter((u) => u.role === filtreRole.value);
});

function formaterDate(iso) {
  if (!iso) return "Jamais connecté";
  return new Date(iso).toLocaleString("fr-FR", { day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit" });
}

async function basculerStatut(u) {
  try {
    if (u.actif) await utilisateurs.desactiver(u.id);
    else await utilisateurs.activer(u.id);
  } catch (e) {
    utilisateurs.erreur = e?.message ?? "Action impossible";
  }
}

const formulaireOuvert = ref(false);
const vide = () => ({ nom: "", prenom: "", identifiant: "", mot_de_passe: "", role: "technicien", site_id: "", courriel: "" });
const nouveau = ref(vide());
const erreurFormulaire = ref(null);

async function soumettre() {
  erreurFormulaire.value = null;
  try {
    await utilisateurs.creer({
      ...nouveau.value,
      site_id: nouveau.value.site_id ? Number(nouveau.value.site_id) : null,
      courriel: nouveau.value.courriel || null,
    });
    formulaireOuvert.value = false;
    nouveau.value = vide();
  } catch (e) {
    erreurFormulaire.value = e?.message ?? "Impossible de créer ce compte";
  }
}
</script>

<template>
  <div>
    <div v-if="utilisateurs.erreur" class="banner err">{{ utilisateurs.erreur }}</div>

    <div class="filters">
      <button class="seg" :class="{ on: filtre === 'actifs' }" @click="filtre = 'actifs'">Actifs · {{ utilisateurs.actifs.length }}</button>
      <button class="seg" :class="{ on: filtre === 'desactives' }" @click="filtre = 'desactives'">Désactivés · {{ utilisateurs.desactives.length }}</button>
      <select v-model="filtreRole" class="inp" style="width: auto; margin-left: 8px">
        <option value="Tous">Tous les rôles</option>
        <option v-for="r in ROLES" :key="r.valeur" :value="r.valeur">{{ r.libelle }}</option>
      </select>
      <span style="flex: 1"></span>
      <button class="btn pri sm" style="width: auto" @click="formulaireOuvert = !formulaireOuvert">
        <Icone nom="plus" taille="sm" />Inviter un utilisateur
      </button>
    </div>

    <div v-if="formulaireOuvert" class="card">
      <div class="ch"><h3>Nouveau compte</h3></div>
      <div class="cb">
        <div class="grid2">
          <div>
            <label class="f">Nom</label><input v-model="nouveau.nom" class="inp" />
            <label class="f">Prénom</label><input v-model="nouveau.prenom" class="inp" />
            <label class="f">Identifiant</label><input v-model="nouveau.identifiant" class="inp" placeholder="p.nom" />
            <label class="f">Mot de passe</label><input v-model="nouveau.mot_de_passe" type="password" class="inp" />
          </div>
          <div>
            <label class="f">Rôle</label>
            <select v-model="nouveau.role" class="inp">
              <option v-for="r in ROLES" :key="r.valeur" :value="r.valeur">{{ r.libelle }}</option>
            </select>
            <label class="f">Site (facultatif)</label>
            <select v-model="nouveau.site_id" class="inp">
              <option value="">Aucun</option>
              <option v-for="s in utilisateurs.sites" :key="s.id" :value="s.id">{{ s.nom }}</option>
            </select>
            <label class="f">Courriel (facultatif)</label>
            <input v-model="nouveau.courriel" type="email" class="inp" />
          </div>
        </div>
        <div v-if="erreurFormulaire" class="banner err" style="margin-top: 8px">{{ erreurFormulaire }}</div>
        <button class="btn pri" style="width: auto; margin-top: 10px" @click="soumettre">Créer le compte</button>
      </div>
    </div>

    <div class="card" style="margin-bottom: 14px">
      <div class="ch"><Icone nom="users" style="color: var(--navy2)" /><h3>Utilisateurs</h3></div>
      <table>
        <thead><tr><th>Nom</th><th>Identifiant</th><th>Rôle</th><th>Site</th><th>Dernière connexion</th><th>Statut</th><th></th></tr></thead>
        <tbody>
          <tr v-for="u in listeFiltree" :key="u.id" :style="!u.actif ? 'opacity:.65' : ''">
            <td><b>{{ u.prenom }} {{ u.nom }}</b></td>
            <td>{{ u.identifiant }}</td>
            <td><span class="tag" :class="roleInfo(u.role).tag">{{ roleInfo(u.role).libelle }}</span></td>
            <td>{{ utilisateurs.nomSite(u.site_id) ?? "—" }}</td>
            <td>{{ formaterDate(u.derniere_connexion) }}</td>
            <td><span class="tag" :class="u.actif ? 't-gr' : 't-gy'">{{ u.actif ? "Actif" : "Désactivé" }}</span></td>
            <td>
              <button class="btn gh sm" style="width: auto" @click="basculerStatut(u)">
                {{ u.actif ? "Désactiver" : "Réactiver" }}
              </button>
            </td>
          </tr>
          <tr v-if="!utilisateurs.chargement && !listeFiltree.length"><td colspan="7" style="color: var(--mut)">Aucun compte.</td></tr>
        </tbody>
      </table>
      <div class="pagin"><span>{{ listeFiltree.length }} compte{{ listeFiltree.length > 1 ? "s" : "" }}</span></div>
    </div>

    <div class="card">
      <div class="ch"><Icone nom="lock" style="color: var(--navy2)" /><h3>Rôles et périmètres</h3></div>
      <table>
        <thead><tr><th>Rôle</th><th>Périmètre</th></tr></thead>
        <tbody>
          <tr v-for="m in MATRICE" :key="m.role">
            <td><b>{{ m.role }}</b></td>
            <td>{{ m.perimetre }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

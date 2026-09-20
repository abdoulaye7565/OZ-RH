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
 * 2. Nouvelle route backend utilisée : `POST /auth/utilisateurs/{id}
 *    /desactiver` et `.../activer` (ajoutées pour cet écran — aucune route
 *    de modification n'existait, seule la création, voir docs/JOURNAL.md).
 *
 * « Gestion des rôles » ajoutée le 2026-09-10 (retour direct de
 * l'utilisateur — "je ne vois pas la gestion des rôles") : la matrice
 * "Rôles et périmètres" ci-dessous était jusque-là un tableau statique de 5
 * lignes recopié de CLAUDE.md §6. Remplacée par la VRAIE matrice permissions
 * × rôles (`GET /api/v1/roles`, lue par introspection de
 * `core/permissions.py` — ~20 permissions réellement vérifiées par les
 * routes, pas une illustration). Toute permission ajoutée à un futur module
 * apparaît ici automatiquement, sans double maintenance. Lecture seule,
 * volontairement : les rôles sont un ensemble fermé de 5 valeurs (CLAUDE.md
 * §6) et les permissions sont du code, pas des données de configuration —
 * les rendre éditables serait un changement d'architecture (RBAC
 * dynamique), pas un correctif d'affichage.
 *
 * Modification du profil ajoutée le 2026-09-09 (retour direct de
 * l'utilisateur, "nous devons permettre la modification") : nouvelle route
 * `PATCH /auth/utilisateurs/{id}` (schemas/auth.py, UtilisateurModification)
 * — ni l'identifiant ni le mot de passe ne s'y changent, volontairement (voir
 * le commentaire du schéma) ; un formulaire séparé de réinitialisation de
 * mot de passe reste à faire si le besoin se confirme, pas construit ici.
 *
 * Formulaires en fenêtre modale (2026-09-09, retour direct de l'utilisateur
 * — voir components/Modal.vue) : écran pilote de cette conversion, avant de
 * la déployer sur le reste des écrans desktop.
 */
import { computed, onMounted, ref } from "vue";
import BarrePagination from "../components/BarrePagination.vue";
import Icone from "../components/Icone.vue";
import Modal from "../components/Modal.vue";
import { useRechercheEtPagination } from "../composables/useRechercheEtPagination";
import { useRolesStore } from "../stores/roles";
import { useUtilisateursStore } from "../stores/utilisateurs";

const utilisateurs = useUtilisateursStore();
onMounted(() => utilisateurs.charger());

// Gestion des rôles (2026-09-10) : matrice réelle, lue depuis le backend.
// Même store que GestionLayout.vue (barre latérale) — une seule source, un
// seul chargement par session, jamais deux copies qui pourraient diverger.
const rolesStore = useRolesStore();
onMounted(() => rolesStore.charger());
const roles = computed(() => rolesStore.donnees);
const erreurRoles = computed(() => rolesStore.erreur);

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

const filtre = ref("actifs"); // "actifs" | "desactives"
const filtreRole = ref("Tous");
const listeFiltree = computed(() => {
  const base = filtre.value === "actifs" ? utilisateurs.actifs : utilisateurs.desactives;
  return filtreRole.value === "Tous" ? base : base.filter((u) => u.role === filtreRole.value);
});

function correspond(u, terme) {
  return (
    `${u.prenom} ${u.nom}`.toLowerCase().includes(terme) ||
    u.identifiant?.toLowerCase().includes(terme) ||
    roleInfo(u.role).libelle.toLowerCase().includes(terme) ||
    (utilisateurs.nomSite(u.site_id) ?? "").toLowerCase().includes(terme)
  );
}
const { recherche, page, totalPages, resultats, elementsPage, allerPage } =
  useRechercheEtPagination(listeFiltree, correspond, 12);

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

// null | "creation" | "edition" — un seul formulaire à la fois, la carte
// change de forme selon le mode plutôt que d'avoir deux cartes séparées.
const modeFormulaire = ref(null);
const videCreation = () => ({ nom: "", prenom: "", identifiant: "", mot_de_passe: "", role: "technicien", site_id: "", courriel: "" });
const nouveau = ref(videCreation());
const idEnEdition = ref(null);
const edition = ref({ nom: "", prenom: "", role: "technicien", site_id: "", courriel: "" });
const erreurFormulaire = ref(null);

function ouvrirCreation() {
  modeFormulaire.value = "creation";
  nouveau.value = videCreation();
  erreurFormulaire.value = null;
}

function ouvrirEdition(u) {
  modeFormulaire.value = "edition";
  idEnEdition.value = u.id;
  edition.value = { nom: u.nom, prenom: u.prenom, role: u.role, site_id: u.site_id ?? "", courriel: u.courriel ?? "" };
  erreurFormulaire.value = null;
}

function fermerFormulaire() {
  modeFormulaire.value = null;
  erreurFormulaire.value = null;
}

async function soumettreCreation() {
  erreurFormulaire.value = null;
  try {
    await utilisateurs.creer({
      ...nouveau.value,
      site_id: nouveau.value.site_id ? Number(nouveau.value.site_id) : null,
      courriel: nouveau.value.courriel || null,
    });
    fermerFormulaire();
  } catch (e) {
    erreurFormulaire.value = e?.message ?? "Impossible de créer ce compte";
  }
}

async function soumettreEdition() {
  erreurFormulaire.value = null;
  try {
    await utilisateurs.modifier(idEnEdition.value, {
      nom: edition.value.nom,
      prenom: edition.value.prenom,
      role: edition.value.role,
      site_id: edition.value.site_id ? Number(edition.value.site_id) : null,
      courriel: edition.value.courriel || null,
    });
    fermerFormulaire();
  } catch (e) {
    // Message serveur direct (ex. "Vous ne pouvez pas retirer votre propre
    // rôle d'administrateur") — pas de reformulation générique qui le perdrait.
    erreurFormulaire.value = e?.message ?? "Impossible de modifier ce compte";
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
      <button class="btn pri sm" style="width: auto" @click="ouvrirCreation">
        <Icone nom="plus" taille="sm" />Inviter un utilisateur
      </button>
    </div>

    <Modal v-if="modeFormulaire === 'creation'" titre="Nouveau compte" @fermer="fermerFormulaire">
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
      <div style="display: flex; gap: 8px; margin-top: 10px">
        <button class="btn pri" style="width: auto" @click="soumettreCreation">Créer le compte</button>
        <button class="btn gh" style="width: auto" @click="fermerFormulaire">Annuler</button>
      </div>
    </Modal>

    <Modal v-if="modeFormulaire === 'edition'" titre="Modifier le compte" @fermer="fermerFormulaire">
      <div class="grid2">
        <div>
          <label class="f">Nom</label><input v-model="edition.nom" class="inp" />
          <label class="f">Prénom</label><input v-model="edition.prenom" class="inp" />
          <label class="f">Courriel (facultatif)</label>
          <input v-model="edition.courriel" type="email" class="inp" />
        </div>
        <div>
          <label class="f">Rôle</label>
          <select v-model="edition.role" class="inp">
            <option v-for="r in ROLES" :key="r.valeur" :value="r.valeur">{{ r.libelle }}</option>
          </select>
          <label class="f">Site (facultatif)</label>
          <select v-model="edition.site_id" class="inp">
            <option value="">Aucun</option>
            <option v-for="s in utilisateurs.sites" :key="s.id" :value="s.id">{{ s.nom }}</option>
          </select>
        </div>
      </div>
      <div v-if="erreurFormulaire" class="banner err" style="margin-top: 8px">{{ erreurFormulaire }}</div>
      <div style="display: flex; gap: 8px; margin-top: 10px">
        <button class="btn pri" style="width: auto" @click="soumettreEdition">Enregistrer</button>
        <button class="btn gh" style="width: auto" @click="fermerFormulaire">Annuler</button>
      </div>
    </Modal>

    <div class="card" style="margin-bottom: 14px">
      <div class="ch">
        <Icone nom="users" style="color: var(--navy2)" /><h3>Utilisateurs</h3>
        <span style="flex: 1"></span>
        <div class="srch">
          <Icone nom="search" taille="sm" />
          <input v-model="recherche" placeholder="Rechercher un nom, un identifiant…" />
        </div>
      </div>
      <table>
        <thead><tr><th>Nom</th><th>Identifiant</th><th>Rôle</th><th>Site</th><th>Dernière connexion</th><th>Statut</th><th></th></tr></thead>
        <tbody>
          <tr v-for="u in elementsPage" :key="u.id" :style="!u.actif ? 'opacity:.65' : ''">
            <td><b>{{ u.prenom }} {{ u.nom }}</b></td>
            <td>{{ u.identifiant }}</td>
            <td><span class="tag" :class="roleInfo(u.role).tag">{{ roleInfo(u.role).libelle }}</span></td>
            <td>{{ utilisateurs.nomSite(u.site_id) ?? "—" }}</td>
            <td>{{ formaterDate(u.derniere_connexion) }}</td>
            <td><span class="tag" :class="u.actif ? 't-gr' : 't-gy'">{{ u.actif ? "Actif" : "Désactivé" }}</span></td>
            <td style="white-space: nowrap">
              <button class="btn gh sm" style="width: auto" @click="ouvrirEdition(u)">Modifier</button>
              <button class="btn gh sm" style="width: auto; margin-left: 6px" @click="basculerStatut(u)">
                {{ u.actif ? "Désactiver" : "Réactiver" }}
              </button>
            </td>
          </tr>
          <tr v-if="!utilisateurs.chargement && !listeFiltree.length"><td colspan="7" style="color: var(--mut)">Aucun compte.</td></tr>
          <tr v-if="listeFiltree.length && !resultats.length"><td colspan="7" style="color: var(--mut)">Aucun compte ne correspond à la recherche.</td></tr>
        </tbody>
      </table>
      <BarrePagination :page="page" :total-pages="totalPages" @changer="allerPage">
        {{ resultats.length }} compte{{ resultats.length > 1 ? "s" : "" }}
      </BarrePagination>
    </div>

    <div v-if="erreurRoles" class="banner err">{{ erreurRoles }}</div>

    <div class="card" style="margin-bottom: 14px">
      <div class="ch"><Icone nom="lock" style="color: var(--navy2)" /><h3>Rôles et périmètres</h3></div>
      <table v-if="roles">
        <thead><tr><th>Rôle</th><th>Périmètre</th></tr></thead>
        <tbody>
          <tr v-for="r in roles.roles" :key="r.valeur">
            <td><b>{{ r.libelle }}</b></td>
            <td>{{ r.perimetre }}</td>
          </tr>
        </tbody>
      </table>
      <div v-else class="skel" style="height: 120px"></div>
    </div>

    <div class="card">
      <div class="ch">
        <Icone nom="lock" style="color: var(--navy2)" /><h3>Permissions par rôle</h3>
        <span style="flex: 1"></span>
        <span class="sub">{{ roles?.permissions.length ?? 0 }} permissions vérifiées par les routes</span>
      </div>
      <div v-if="roles" style="overflow-x: auto">
        <table>
          <thead>
            <tr>
              <th>Permission</th>
              <th v-for="r in roles.roles" :key="r.valeur" style="text-align: center; white-space: nowrap">{{ r.libelle }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="p in roles.permissions" :key="p.cle">
              <td>{{ p.libelle }}</td>
              <td v-for="r in roles.roles" :key="r.valeur" style="text-align: center">
                <Icone v-if="p.roles.includes(r.valeur)" nom="check" taille="sm" style="color: var(--green)" />
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-else class="skel" style="height: 200px"></div>
    </div>
  </div>
</template>

<script setup>
/**
 * Coffre-fort — vue desktop (maquette #p-vault, CDC section 5.2.4).
 *
 * Écart assumé : la maquette montre un journal global (toutes lignes de
 * tous les secrets confondues). Le CDC (5.2.4, "Fonctionnalités attendues")
 * est plus précis : "Consulter le journal des accès À UN SECRET DONNÉ" —
 * singulier, pas un flux global. La route backend suit ce libellé
 * (`GET /secrets/{id}/journal`, pas de route d'agrégation). Le panneau de
 * droite affiche donc le journal du secret sélectionné (clic sur une
 * ligne), pas un flux de tous les accès — fidèle au texte du CDC plutôt
 * qu'à l'aspect de la maquette, qui reste illustratif sur ce point précis.
 */
import { computed, onBeforeUnmount, onMounted, ref } from "vue";
import BarrePagination from "../components/BarrePagination.vue";
import Icone from "../components/Icone.vue";
import Modal from "../components/Modal.vue";
import { useRechercheEtPagination } from "../composables/useRechercheEtPagination";
import { useAuthStore } from "../stores/auth";
import { DELAI_MASQUAGE_MS, ROLES_SECRET, TYPES_ACCES, useSecretsStore } from "../stores/secrets";

const auth = useAuthStore();
const secrets = useSecretsStore();
onMounted(() => secrets.charger());

const peutGerer = computed(() => ["responsable", "administrateur"].includes(auth.utilisateur?.role));

function correspond(s, terme) {
  return (
    s.libelle?.toLowerCase().includes(terme) ||
    s.identifiant?.toLowerCase().includes(terme) ||
    (s.equipement_id ? (secrets.nomEquipement(s.equipement_id) ?? "") : "").toLowerCase().includes(terme)
  );
}
const { recherche, page, totalPages, resultats, elementsPage, allerPage } =
  useRechercheEtPagination(computed(() => secrets.liste), correspond, 15);

const revelations = ref({});
async function basculerAffichage(secret) {
  if (revelations.value[secret.id]) {
    clearTimeout(revelations.value[secret.id].minuteur);
    delete revelations.value[secret.id];
    return;
  }
  try {
    const valeur = await secrets.consulter(secret.id);
    const minuteur = setTimeout(() => {
      delete revelations.value[secret.id];
    }, DELAI_MASQUAGE_MS);
    revelations.value[secret.id] = { valeur, minuteur };
  } catch (e) {
    secrets.erreur = e?.message ?? "Impossible de consulter ce secret";
  }
}
onBeforeUnmount(() => {
  for (const r of Object.values(revelations.value)) clearTimeout(r.minuteur);
});

function libelleType(valeur) {
  return TYPES_ACCES.find((t) => t.valeur === valeur)?.libelle ?? valeur;
}
function formaterDateCourte(iso) {
  return new Date(iso).toLocaleDateString("fr-FR", { day: "2-digit", month: "2-digit" });
}
function formaterDateHeure(iso) {
  return new Date(iso).toLocaleString("fr-FR", { day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit" });
}
const LIBELLE_ACTION = { consultation: "consultation", creation: "création", modification: "modification" };

const secretSelectionne = ref(null);
async function selectionner(secret) {
  if (!peutGerer.value) return; // GET .../journal est réservé à responsable+administrateur (CONSULTER_JOURNAL_SECRETS)
  secretSelectionne.value = secret;
  try {
    await secrets.chargerJournal(secret.id);
  } catch (e) {
    secrets.erreur = e?.message ?? "Impossible de charger le journal de ce secret";
  }
}
const journalAffiche = computed(() => (secretSelectionne.value ? secrets.journal[secretSelectionne.value.id] ?? [] : []));

const formulaireOuvert = ref(false);
const vide = () => ({ libelle: "", equipement_id: "", type_acces: "administration", identifiant: "", valeur: "", role_requis: "technicien" });
const nouveau = ref(vide());
const erreurFormulaire = ref(null);
const generationEnCours = ref(false);

async function genererMotDePasse() {
  generationEnCours.value = true;
  try {
    nouveau.value.valeur = await secrets.genererMotDePasse();
  } catch (e) {
    erreurFormulaire.value = e?.message ?? "Impossible de générer un mot de passe";
  } finally {
    generationEnCours.value = false;
  }
}
async function soumettre() {
  erreurFormulaire.value = null;
  try {
    await secrets.creer({ ...nouveau.value, equipement_id: nouveau.value.equipement_id || null });
    formulaireOuvert.value = false;
    nouveau.value = vide();
  } catch (e) {
    erreurFormulaire.value = e?.message ?? "Impossible d'enregistrer ce secret";
  }
}
</script>

<template>
  <div>
    <div class="banner err">
      <Icone nom="lock" taille="sm" style="margin-top: 1px" />
      <div><b>Zone à accès restreint.</b> Toute consultation est enregistrée au journal d'audit avec votre identité et l'horodatage. Les secrets sont chiffrés au repos et ne figurent jamais dans les sauvegardes en clair.</div>
    </div>
    <div v-if="secrets.erreur" class="banner err">{{ secrets.erreur }}</div>

    <Modal v-if="formulaireOuvert" titre="Nouveau secret" @fermer="formulaireOuvert = false">
      <div class="grid2">
        <div>
          <label class="f">Libellé</label><input v-model="nouveau.libelle" class="inp" placeholder="Ex. Admin RouterOS" />
          <label class="f">Équipement (facultatif)</label>
          <select v-model="nouveau.equipement_id" class="inp">
            <option value="">Aucun</option>
            <option v-for="e in secrets.equipements" :key="e.id" :value="e.id">{{ e.identity }}</option>
          </select>
          <label class="f">Type d'accès</label>
          <select v-model="nouveau.type_acces" class="inp">
            <option v-for="t in TYPES_ACCES" :key="t.valeur" :value="t.valeur">{{ t.libelle }}</option>
          </select>
        </div>
        <div>
          <label class="f">Identifiant (facultatif)</label><input v-model="nouveau.identifiant" class="inp" placeholder="Ex. admin" />
          <label class="f">Valeur du secret</label>
          <div style="display: flex; gap: 6px">
            <input v-model="nouveau.valeur" class="inp" placeholder="Mot de passe, clé…" />
            <button class="btn gh sm" style="width: auto; white-space: nowrap" :disabled="generationEnCours" @click="genererMotDePasse">Générer</button>
          </div>
          <label class="f">Rôle minimal requis</label>
          <select v-model="nouveau.role_requis" class="inp">
            <option v-for="r in ROLES_SECRET" :key="r.valeur" :value="r.valeur">{{ r.libelle }}</option>
          </select>
        </div>
      </div>
      <div v-if="erreurFormulaire" class="banner err" style="margin-top: 8px">{{ erreurFormulaire }}</div>
      <div style="display: flex; gap: 8px; margin-top: 10px">
        <button class="btn pri" style="width: auto" @click="soumettre">Enregistrer</button>
        <button class="btn gh" style="width: auto" @click="formulaireOuvert = false">Annuler</button>
      </div>
    </Modal>

    <div class="split">
      <div class="card">
        <div class="ch">
          <Icone nom="key" style="color: var(--navy2)" /><h3>Secrets enregistrés</h3>
          <span style="flex: 1"></span>
          <div class="srch">
            <Icone nom="search" taille="sm" />
            <input v-model="recherche" placeholder="Rechercher un secret, un équipement…" />
          </div>
          <span v-if="peutGerer" class="r" style="cursor: pointer" role="button" tabindex="0" @click="formulaireOuvert = true" @keydown.enter="formulaireOuvert = true">
            Ajouter un secret
          </span>
        </div>
        <table>
          <thead><tr><th>Équipement / Libellé</th><th>Type</th><th>Identifiant</th><th>Secret</th><th>Modifié</th><th>Rôle requis</th></tr></thead>
          <tbody>
            <tr v-for="s in elementsPage" :key="s.id" :style="peutGerer ? 'cursor: pointer' : ''" @click="selectionner(s)">
              <td>
                <div class="cellrow">
                  <span class="mini m-nv"><Icone nom="key" taille="sm" /></span>
                  <div><b>{{ s.equipement_id ? secrets.nomEquipement(s.equipement_id) : s.libelle }}</b><div class="sub">{{ s.equipement_id ? s.libelle : "" }}</div></div>
                </div>
              </td>
              <td>{{ libelleType(s.type_acces) }}</td>
              <td>{{ s.identifiant || "—" }}</td>
              <td>
                <div class="cellrow">
                  <code style="background: var(--surface2); border: 1px solid var(--line); border-radius: 5px; padding: 3px 8px; font-size: 11.5px; letter-spacing: 1.5px">
                    {{ revelations[s.id] ? revelations[s.id].valeur : "••••••••" }}
                  </code>
                  <button class="btn gh sm" style="width: auto" @click.stop="basculerAffichage(s)"><Icone nom="eye" taille="sm" /></button>
                </div>
              </td>
              <td>{{ formaterDateCourte(s.modifie_le) }}</td>
              <td><span class="tag" :class="secrets.infoRole(s.role_requis).tag">{{ secrets.infoRole(s.role_requis).libelle }}</span></td>
            </tr>
            <tr v-if="!secrets.chargement && !secrets.liste.length"><td colspan="6" style="color: var(--mut)">Aucun secret accessible à votre rôle.</td></tr>
            <tr v-if="secrets.liste.length && !resultats.length"><td colspan="6" style="color: var(--mut)">Aucun secret ne correspond à la recherche.</td></tr>
          </tbody>
        </table>
        <BarrePagination :page="page" :total-pages="totalPages" @changer="allerPage">
          {{ resultats.length }} sur {{ secrets.liste.length }} secret{{ secrets.liste.length > 1 ? "s" : "" }} · 2FA recommandée sur les comptes cloud
        </BarrePagination>
      </div>

      <div class="card">
        <div class="ch"><Icone nom="clock" style="color: var(--navy2)" /><h3>Journal des accès</h3></div>
        <div class="cb">
          <p v-if="!peutGerer" style="font-size: 12.5px; color: var(--mut)">Réservé au responsable et à l'administrateur.</p>
          <p v-else-if="!secretSelectionne" style="font-size: 12.5px; color: var(--mut)">Cliquez sur un secret pour consulter son journal.</p>
          <template v-else>
            <p style="font-size: 12px; color: var(--mut); margin-bottom: 10px"><b>{{ secretSelectionne.libelle }}</b></p>
            <div class="timeline">
              <div v-for="j in journalAffiche" :key="j.id" class="tl">
                <b>{{ secrets.nomUtilisateur(j.utilisateur_id) ?? `Utilisateur #${j.utilisateur_id}` }}</b>
                <span>{{ formaterDateHeure(j.horodatage) }} · {{ LIBELLE_ACTION[j.action] ?? j.action }}</span>
              </div>
              <p v-if="!journalAffiche.length" style="font-size: 12px; color: var(--mut)">Aucun accès enregistré.</p>
            </div>
          </template>
          <div class="banner warn" style="margin: 12px 0 0">
            <Icone nom="alert" taille="sm" style="margin-top: 1px" />
            <div>Le journal est conservé et ne peut être ni modifié ni supprimé, y compris par un administrateur.</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

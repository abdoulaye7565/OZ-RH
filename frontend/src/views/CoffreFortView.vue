<script setup>
/**
 * Coffre-fort — vue mobile (maquette #s-vault, CDC section 5.2.4).
 *
 * Chaque secret est masqué par défaut ; l'afficher appelle
 * POST /secrets/{id}/consulter (déchiffre ET journalise côté serveur dans
 * le même appel — jamais l'un sans l'autre) puis se masque automatiquement
 * après 15 secondes, comme l'exige la maquette et la règle 5.2.4 ("délai
 * paramétrable de quelques secondes"). La valeur en clair ne vit que dans
 * `revelations` (état local du composant), jamais dans le store Pinia au-
 * delà de l'appel — un changement d'écran l'efface immédiatement.
 */
import { computed, onBeforeUnmount, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import Icone from "../components/Icone.vue";
import Modal from "../components/Modal.vue";
import BandeauReseau from "../components/BandeauReseau.vue";
import { useAuthStore } from "../stores/auth";
import { DELAI_MASQUAGE_MS, ROLES_SECRET, TYPES_ACCES, useSecretsStore } from "../stores/secrets";

const router = useRouter();
const auth = useAuthStore();
const secrets = useSecretsStore();
onMounted(() => secrets.charger());

const peutGerer = computed(() => ["responsable", "administrateur"].includes(auth.utilisateur?.role));

// secret_id -> { valeur, minuteur }
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

// --- Nouveau secret ---
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
  <div class="ecran-mobile">
    <div class="net online"><Icone nom="wifi" taille="sm" />En ligne<span class="sp">Accès journalisé</span></div>
    <header class="hd">
      <button class="back" aria-label="Retour" @click="router.push({ name: 'menu' })"><Icone nom="back" /></button>
      <div>
        <h1>Coffre-fort</h1>
        <div class="sub">Chiffré · rôle requis</div>
      </div>
    </header>

    <div class="wrap">
      <div class="body">
        <div class="pad">
          <div v-if="secrets.erreur" class="banner err">{{ secrets.erreur }}</div>
          <div v-else-if="secrets.chargement" class="skel" style="height: 64px"></div>

          <div v-for="s in secrets.liste" :key="s.id" class="vault">
            <div style="display: flex; gap: 9px; align-items: center; justify-content: space-between">
              <div style="display: flex; gap: 9px; align-items: center">
                <span class="lead nv"><Icone nom="key" /></span>
                <div>
                  <b style="font-size: 13.5px; font-weight: 650">{{ s.equipement_id ? secrets.nomEquipement(s.equipement_id) : s.libelle }}</b>
                  <div style="font-size: 11.5px; color: var(--mut)">
                    {{ s.identifiant ? `${s.identifiant} · ` : "" }}{{ libelleType(s.type_acces) }}
                  </div>
                </div>
              </div>
              <span class="tag" :class="secrets.infoRole(s.role_requis).tag">{{ secrets.infoRole(s.role_requis).libelle }}</span>
            </div>
            <div class="secret">
              <code>{{ revelations[s.id] ? revelations[s.id].valeur : "••••••••••••" }}</code>
              <button class="eye" :aria-label="revelations[s.id] ? 'Masquer' : 'Afficher'" @click="basculerAffichage(s)">
                <Icone nom="eye" />
              </button>
            </div>
          </div>

          <div v-if="!secrets.chargement && !secrets.liste.length" class="empty">
            <div class="ic"><Icone nom="key" taille="lg" /></div>
            <b>Aucun secret accessible à votre rôle</b>
          </div>

          <div class="banner info">
            <Icone nom="clock" taille="sm" style="margin-top: 1px" />
            <div>Chaque affichage est tracé (qui, quand, quel secret) et se masque après 15 secondes.</div>
          </div>

          <template v-if="peutGerer">
            <button class="btn pri" @click="formulaireOuvert = true">
              <Icone nom="plus" taille="sm" />Ajouter un secret
            </button>

            <Modal v-if="formulaireOuvert" titre="Ajouter un secret" @fermer="formulaireOuvert = false">
              <label class="f">Libellé</label>
              <input v-model="nouveau.libelle" class="inp" placeholder="Ex. Admin RouterOS" />
              <label class="f">Équipement (facultatif)</label>
              <select v-model="nouveau.equipement_id" class="inp">
                <option value="">Aucun</option>
                <option v-for="e in secrets.equipements" :key="e.id" :value="e.id">{{ e.identity }}</option>
              </select>
              <label class="f">Type d'accès</label>
              <select v-model="nouveau.type_acces" class="inp">
                <option v-for="t in TYPES_ACCES" :key="t.valeur" :value="t.valeur">{{ t.libelle }}</option>
              </select>
              <label class="f">Identifiant (facultatif)</label>
              <input v-model="nouveau.identifiant" class="inp" placeholder="Ex. admin" />
              <label class="f">Valeur du secret</label>
              <div style="display: flex; gap: 6px">
                <input v-model="nouveau.valeur" class="inp" placeholder="Mot de passe, clé…" />
                <button class="btn gh sm" style="width: auto; white-space: nowrap" :disabled="generationEnCours" @click="genererMotDePasse">Générer</button>
              </div>
              <label class="f">Rôle minimal requis</label>
              <select v-model="nouveau.role_requis" class="inp">
                <option v-for="r in ROLES_SECRET" :key="r.valeur" :value="r.valeur">{{ r.libelle }}</option>
              </select>
              <div v-if="erreurFormulaire" class="banner err" style="margin-top: 8px">{{ erreurFormulaire }}</div>
              <div class="btnrow" style="margin-top: 10px">
                <button class="btn pri sm" style="width: auto" @click="soumettre">Enregistrer</button>
                <button class="btn gh sm" style="width: auto" @click="formulaireOuvert = false">Annuler</button>
              </div>
            </Modal>
          </template>

          <div style="height: 56px"></div>
        </div>
      </div>
    </div>

    <nav class="tabs">
      <button class="tb" @click="router.push({ name: 'accueil' })"><Icone nom="home" />Accueil</button>
      <button class="tb" @click="router.push({ name: 'signalements' })"><Icone nom="alert" />Signaux</button>
      <button class="tb" @click="router.push({ name: 'slam' })"><Icone nom="climb" />SLAM</button>
      <button class="tb" @click="router.push({ name: 'tableau-de-bord' })"><Icone nom="chart" />Tableau</button>
      <button class="tb" @click="router.push({ name: 'menu' })"><Icone nom="grid" />Menu</button>
    </nav>
  </div>
</template>

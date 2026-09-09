/**
 * Classement des documents par dossier réel du SMI (voir
 * `SMI-SHEQ_Hirondelles_IT_Lab/LISEZ-MOI.txt` fourni par l'utilisateur —
 * l'arborescence exacte du classeur documentaire papier/bureautique
 * d'Hirondelles IT Lab, reprise ici pour l'écran Documents).
 *
 * Aucun champ "dossier" n'existe sur le modèle Document (backend) : le
 * classement réel n'est pas arbitraire, il découle entièrement de trois
 * champs déjà là (niveau, confidentialite, statut) — la même règle que le
 * classeur papier applique (niveau 1 → 01-Politique, niveau 4 confidentiel →
 * 04.../CONFIDENTIEL, une version retirée → 09-Archives). Calculé ici plutôt
 * qu'ajouté en base : pas de nouveau champ à tenir synchronisé avec des
 * données qui l'impliquent déjà.
 *
 * 05 à 08 sont d'authentiques dossiers du classeur réel, mais qui
 * n'accueillent pas de DOCUMENT au sens de ce module (05-Enregistrements
 * accueille les fiches remplies — signalements, permis, inspections...,
 * modélisées par leurs propres entités, pas par Document ; 06 et 07 sont des
 * dossiers de classement de justificatifs, sans registre applicatif dédié ;
 * 08 est une bibliothèque de textes externes, hors périmètre applicatif).
 * Listés quand même, vides, pour que la structure réelle du SMI soit
 * visible en entier — pas seulement les dossiers qui se trouvent avoir des
 * lignes en base aujourd'hui.
 */
export const DOSSIERS = [
  { cle: "01-politique", nom: "01 · Politique et engagement", abrege: "01 · Politique", description: "Politique SHEQ signée par la direction (niveau 1)" },
  { cle: "02-pilotage", nom: "02 · Pilotage", abrege: "02 · Pilotage", description: "Liste maîtresse, registres, plan d'action, tableau de bord (niveau 2)" },
  { cle: "03-procedures", nom: "03 · Procédures et consignes", abrege: "03 · Procédures", description: "Procédures et modes opératoires (niveau 3)" },
  { cle: "04-formulaires", nom: "04 · Formulaires vierges", abrege: "04 · Formulaires", description: "Formulaires FOR-SHEQ à imprimer/dupliquer (niveau 4)" },
  { cle: "04-formulaires-confidentiel", nom: "04 · Formulaires vierges / CONFIDENTIEL", abrege: "04 · CONFIDENTIEL", description: "Fiches de configuration contenant des identifiants : accès restreint" },
  { cle: "05-enregistrements", nom: "05 · Enregistrements", abrege: "05 · Enregistrements", description: "Fiches remplies (signalements, permis, inspections…) — pas des Document ici, voir leurs propres modules" },
  { cle: "06-formations", nom: "06 · Formations et sensibilisations", abrege: "06 · Formations", description: "Supports et feuilles de présence" },
  { cle: "07-revues", nom: "07 · Revues et audits", abrege: "07 · Revues", description: "Comptes rendus de revue de direction et audits internes" },
  { cle: "08-reglementation", nom: "08 · Réglementation et référentiels", abrege: "08 · Réglementation", description: "Textes applicables, normes ISO 45001/14001/9001" },
  { cle: "09-archives", nom: "09 · Archives", abrege: "09 · Archives", description: "Anciennes versions de documents — ne plus utiliser" },
];

export function dossierDe(document) {
  if (document.statut === "archive") return "09-archives";
  if (document.niveau === 1) return "01-politique";
  if (document.niveau === 2) return "02-pilotage";
  if (document.niveau === 3) return "03-procedures";
  if (document.niveau === 4) return document.confidentialite === "confidentiel" ? "04-formulaires-confidentiel" : "04-formulaires";
  return "02-pilotage";
}

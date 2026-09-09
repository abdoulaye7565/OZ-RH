/**
 * `new Date("2026-10-15").toLocaleDateString()` décale parfois d'un jour :
 * une chaîne "AAAA-MM-JJ" (sans heure) est interprétée comme un instant UTC
 * minuit par le constructeur `Date`, puis reformatée dans le fuseau local —
 * qui peut retomber la veille selon le fuseau du navigateur. Trouvé en
 * testant une échéance d'action réelle (saisie 15/10, affichée 14/10).
 *
 * À utiliser pour tout champ de type `date` (échéance, date de vérification,
 * date de mise en service…) — jamais pour un vrai horodatage (`date_saisie`,
 * `cree_le`), qui doit au contraire être converti en heure locale.
 */
export function formaterDateCivile(dateIso) {
  if (!dateIso) return "—";
  const [annee, mois, jour] = dateIso.slice(0, 10).split("-").map(Number);
  return new Date(annee, mois - 1, jour).toLocaleDateString("fr-FR");
}

/** Jours restants avant une date civile (peut être négatif si dépassée). */
export function joursRestantsCivil(dateIso) {
  if (!dateIso) return null;
  const [annee, mois, jour] = dateIso.slice(0, 10).split("-").map(Number);
  const cible = new Date(annee, mois - 1, jour);
  const aujourdhui = new Date();
  aujourdhui.setHours(0, 0, 0, 0);
  return Math.round((cible - aujourdhui) / 86400000);
}

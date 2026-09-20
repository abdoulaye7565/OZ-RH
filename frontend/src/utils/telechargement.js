import api from "../services/api";

/**
 * Télécharge un fichier servi par l'API (export PDF principalement) en
 * conservant l'en-tête Authorization — un simple <a href> ne l'enverrait pas.
 * Ajouté le 2026-09-10 (revue d'ensemble : les PDF officiels générés par le
 * back-end n'étaient récupérables nulle part dans l'interface).
 *
 * @param {string} chemin - chemin API, ex. `/api/v1/permis/12/export-pdf`
 * @param {string} nomFichier - nom proposé à l'enregistrement (ex. `PT-2026-004.pdf`)
 */
export async function telechargerPdf(chemin, nomFichier) {
  const reponse = await api.requete(chemin, { brut: true });
  const blob = await reponse.blob();
  const url = URL.createObjectURL(blob);
  try {
    const lien = document.createElement("a");
    lien.href = url;
    lien.download = nomFichier || "document.pdf";
    document.body.appendChild(lien);
    lien.click();
    lien.remove();
  } finally {
    // Laisser au navigateur le temps de démarrer le téléchargement avant de
    // révoquer l'URL objet.
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }
}

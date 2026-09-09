"""Découpage en segments (prompt 6.2, chapitre 16.2.1 : "découpage en
segments"). Ne coupe pas au milieu d'un mot : regroupe les paragraphes d'une
section jusqu'à la taille cible, plutôt qu'une troncature brute au caractère
près — un segment reste un texte lisible isolément, condition nécessaire à ce
qu'une citation ait un sens pour l'utilisateur."""

TAILLE_CIBLE_CARACTERES = 1500


def decouper(texte: str, taille_cible: int = TAILLE_CIBLE_CARACTERES) -> list[str]:
    paragraphes = [p.strip() for p in texte.split("\n") if p.strip()]
    if not paragraphes:
        return []

    segments: list[str] = []
    segment_courant: list[str] = []
    longueur_courante = 0

    for paragraphe in paragraphes:
        if longueur_courante + len(paragraphe) > taille_cible and segment_courant:
            segments.append("\n".join(segment_courant))
            segment_courant = []
            longueur_courante = 0
        segment_courant.append(paragraphe)
        longueur_courante += len(paragraphe)

    if segment_courant:
        segments.append("\n".join(segment_courant))

    return segments

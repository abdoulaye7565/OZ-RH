"""Stockage des pièces jointes sur le système de fichiers, hors base de données
(point 9 du CDC, exigence non fonctionnelle "pièces jointes")."""
import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile, status

from app.core.config import settings

TYPES_IMAGE_AUTORISES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}
TAILLE_MAX_PHOTO_OCTETS = 5 * 1024 * 1024  # 5 Mo


async def enregistrer_photos(fichiers: list[UploadFile], sous_dossier: str, nombre_max: int) -> list[str]:
    """Valide type et taille, écrit sur disque sous un nom aléatoire (jamais le nom
    fourni par le client), renvoie les chemins relatifs stockés. Lève une
    HTTPException 400 si un fichier ne respecte pas les règles — rien n'est écrit
    sur disque si un seul fichier du lot est invalide (tout ou rien)."""
    if len(fichiers) > nombre_max:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{nombre_max} photos maximum, {len(fichiers)} envoyées",
        )

    contenus: list[tuple[bytes, str]] = []
    for fichier in fichiers:
        extension = TYPES_IMAGE_AUTORISES.get(fichier.content_type or "")
        if extension is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Type de fichier non autorisé : {fichier.content_type}",
            )
        contenu = await fichier.read()
        if len(contenu) > TAILLE_MAX_PHOTO_OCTETS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Photo trop volumineuse : {len(contenu) / 1024 / 1024:.1f} Mo (5 Mo maximum)",
            )
        contenus.append((contenu, extension))

    dossier = Path(settings.storage_dir) / sous_dossier
    dossier.mkdir(parents=True, exist_ok=True)

    chemins: list[str] = []
    for contenu, extension in contenus:
        nom_fichier = f"{uuid.uuid4().hex}{extension}"
        (dossier / nom_fichier).write_bytes(contenu)
        # .as_posix() : chemin stocké avec des "/" quel que soit l'OS du serveur qui
        # écrit (Windows en développement, Linux en conteneur) — sinon un chemin
        # enregistré avec des "\" sous Windows serait invalide relu sous Linux.
        chemins.append((Path(sous_dossier) / nom_fichier).as_posix())

    return chemins

"""Import initial du parc d'équipements (prompt 3.1) depuis un gabarit CSV/XLSX,
sur le modèle du fichier réel docs/INV-SHEQ-001_Inventaire_Parc.xlsx.

Le gabarit réel comporte des colonnes qui ne correspondent à aucun champ du
dictionnaire EQUIPEMENT (7.2.4) : « Adresse IP » (donnée de CONFIGURATION, pas
d'EQUIPEMENT — voir parametres_reseau), « Type d'équipement » (non modélisé,
seuls marque/modèle le sont), « Fiche de configuration (réf.) » et « Dernière
inspection » (dérivées des historiques CONFIGURATION/INSPECTION, jamais des
données saisies). Ces colonnes sont acceptées si présentes mais ignorées,
plutôt que de rejeter le fichier réel tel qu'il existe — signalé dans
docs/JOURNAL.md, pas inventé silencieusement.
"""
import csv
import io
from datetime import date

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.enums import MarqueEquipement, StatutEquipement
from app.models.equipement import Equipement
from app.models.site import Site
from app.schemas.equipement import EquipementCreation, LigneErreurImport, RapportImport
from app.services.equipement_service import creer_equipement, valider_format_identity

# En-têtes exacts du gabarit réel (docs/INV-SHEQ-001_Inventaire_Parc.xlsx, feuille
# "Inventaire", ligne 4) — repris littéralement, pas réinventés.
COLONNES_IGNOREES = {"Type d'équipement", "Adresse IP", "Fiche de configuration (réf.)", "Dernière inspection"}
COLONNES_REQUISES = {
    "Site / Client",
    "Emplacement",
    "Marque",
    "Modèle",
    "N° de série",
    "Identity / Nom",
    "Date d'installation",
}
COLONNES_OPTIONNELLES = {"Adresse MAC", "Fin de garantie", "Statut", "Observations"}

_MARQUES_PAR_LIBELLE = {m.value.lower(): m for m in MarqueEquipement}
_STATUTS_PAR_LIBELLE = {
    "en service": StatutEquipement.EN_SERVICE,
    "en panne": StatutEquipement.EN_PANNE,
    "en maintenance": StatutEquipement.EN_MAINTENANCE,
    "retiré": StatutEquipement.RETIRE,
    "retire": StatutEquipement.RETIRE,
}


def _parser_date(valeur: str, champ: str) -> date:
    """Le gabarit réel utilise le format MM/AAAA (ex. "03/2026"), pas une date
    complète — jour fixé au 1er du mois, faute de jour réel connu. Une date
    complète JJ/MM/AAAA ou AAAA-MM-JJ est aussi acceptée par tolérance."""
    valeur = valeur.strip()
    for fmt, jour_fixe in (("%m/%Y", True), ("%d/%m/%Y", False), ("%Y-%m-%d", False)):
        try:
            from datetime import datetime as _dt

            parsed = _dt.strptime(valeur, fmt)
            return date(parsed.year, parsed.month, 1) if jour_fixe else parsed.date()
        except ValueError:
            continue
    raise ValueError(f"{champ} : date « {valeur} » invalide (formats acceptés : MM/AAAA, JJ/MM/AAAA, AAAA-MM-JJ)")


def _lire_lignes_csv(contenu: bytes) -> list[dict]:
    texte = contenu.decode("utf-8-sig")
    return list(csv.DictReader(io.StringIO(texte)))


def _lire_lignes_xlsx(contenu: bytes) -> list[dict]:
    # openpyxl : nouvelle dépendance (voir requirements.txt et docs/JOURNAL.md,
    # prompt 3.1) — la bibliothèque standard ne lit pas le format XLSX.
    from openpyxl import load_workbook

    classeur = load_workbook(io.BytesIO(contenu), read_only=True, data_only=True)
    feuille = classeur.active
    lignes_brutes = list(feuille.iter_rows(values_only=True))
    if not lignes_brutes:
        return []
    # Le gabarit réel place les en-têtes après des lignes de titre/instructions
    # (ligne 4 dans docs/INV-SHEQ-001_Inventaire_Parc.xlsx) : on cherche la
    # première ligne qui contient au moins toutes les colonnes requises,
    # plutôt que de supposer que la ligne 1 est l'en-tête.
    index_entete = None
    for i, ligne in enumerate(lignes_brutes):
        cellules = {str(c).strip() for c in ligne if c is not None}
        if COLONNES_REQUISES <= cellules:
            index_entete = i
            break
    if index_entete is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"En-têtes attendus introuvables dans le fichier (colonnes requises : {sorted(COLONNES_REQUISES)})",
        )
    entetes = [str(c).strip() if c is not None else "" for c in lignes_brutes[index_entete]]
    resultat = []
    for ligne in lignes_brutes[index_entete + 1 :]:
        if all(c is None for c in ligne):
            continue
        resultat.append({entetes[i]: (str(ligne[i]).strip() if ligne[i] is not None else "") for i in range(len(entetes)) if entetes[i]})
    return resultat


def _construire_equipement(db: Session, ligne: dict, numero_ligne: int) -> tuple[EquipementCreation | None, list[str]]:
    erreurs: list[str] = []

    manquants = [c for c in COLONNES_REQUISES if not (ligne.get(c) or "").strip()]
    if manquants:
        erreurs.append(f"Colonnes obligatoires manquantes : {', '.join(sorted(manquants))}")
        return None, erreurs

    nom_site = ligne["Site / Client"].strip()
    site = db.scalar(select(Site).where(Site.nom.ilike(nom_site)))
    if site is None:
        erreurs.append(f"Site « {nom_site} » introuvable")

    marque = _MARQUES_PAR_LIBELLE.get(ligne["Marque"].strip().lower())
    if marque is None:
        erreurs.append(
            f"Marque « {ligne['Marque']} » inconnue (valeurs acceptées : {', '.join(m.value for m in MarqueEquipement)})"
        )

    try:
        identity = valider_format_identity(ligne["Identity / Nom"])
    except ValueError as exc:
        identity = None
        erreurs.append(str(exc))

    try:
        date_installation = _parser_date(ligne["Date d'installation"], "Date d'installation")
    except ValueError as exc:
        date_installation = None
        erreurs.append(str(exc))

    fin_garantie = None
    valeur_garantie = (ligne.get("Fin de garantie") or "").strip()
    if valeur_garantie:
        try:
            fin_garantie = _parser_date(valeur_garantie, "Fin de garantie")
        except ValueError as exc:
            erreurs.append(str(exc))

    if erreurs:
        return None, erreurs

    return (
        EquipementCreation(
            identity=identity,
            marque=marque,
            modele=ligne["Modèle"].strip(),
            numero_serie=ligne["N° de série"].strip(),
            adresse_mac=(ligne.get("Adresse MAC") or "").strip() or None,
            site_id=site.id,
            emplacement=ligne["Emplacement"].strip(),
            date_installation=date_installation,
            fin_garantie=fin_garantie,
        ),
        [],
    )


def importer_parc(db: Session, contenu: bytes, nom_fichier: str, cree_par_id: int) -> RapportImport:
    if nom_fichier.lower().endswith(".xlsx"):
        lignes = _lire_lignes_xlsx(contenu)
    elif nom_fichier.lower().endswith(".csv"):
        lignes = _lire_lignes_csv(contenu)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Format non pris en charge : CSV ou XLSX attendu"
        )

    equipements_crees = []
    erreurs: list[LigneErreurImport] = []
    identites_du_lot: set[str] = set()

    for numero, ligne in enumerate(lignes, start=1):
        donnees, erreurs_ligne = _construire_equipement(db, ligne, numero)
        if donnees is not None and donnees.identity in identites_du_lot:
            erreurs_ligne = [f"Identity « {donnees.identity} » dupliquée dans le fichier importé"]
            donnees = None
        if donnees is None:
            erreurs.append(
                LigneErreurImport(ligne=numero, identity=(ligne.get("Identity / Nom") or "").strip() or None, erreurs=erreurs_ligne)
            )
            continue
        try:
            equipement = creer_equipement(db, donnees, cree_par_id=cree_par_id)
        except HTTPException as exc:
            erreurs.append(LigneErreurImport(ligne=numero, identity=donnees.identity, erreurs=[str(exc.detail)]))
            continue
        identites_du_lot.add(donnees.identity)
        equipements_crees.append(equipement)

    return RapportImport(
        total_lignes=len(lignes),
        importees=len(equipements_crees),
        en_erreur=len(erreurs),
        equipements=equipements_crees,
        erreurs=erreurs,
    )

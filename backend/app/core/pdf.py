"""Génération PDF partagée par tous les modules exportables (prompts 3.2 et
5.1, chapitre 14 du CDC, cas de test 12 : "Exporter un enregistrement en
PDF — document conforme au modèle du système documentaire, avec sa
référence"). Le CDC ne cite WeasyPrint qu'à titre d'exemple (chapitre 10.2 :
"Bibliothèque Python, ex. : WeasyPrint / ReportLab") — ReportLab retenu, déjà
utilisé depuis le prompt 3.2 et sans dépendance système (contrairement à
WeasyPrint, qui exige GTK/Cairo — pénible sous Windows, l'environnement de
développement de ce projet). Voir docs/JOURNAL.md, prompt 5.1.

Toute la mise en page spécifique à chaque module (ordre des sections, contenu)
reste dans son propre service — ce module ne fournit que les briques
communes (en-tête, tableaux clé/valeur, tableaux libres, pied de page)."""
import io

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

_STYLES = getSampleStyleSheet()
# Cellules de tableau en Paragraph (pas des chaînes brutes) : ReportLab ne
# retourne jamais à la ligne une chaîne brute qui dépasse la largeur de
# colonne, le texte est simplement rogné visuellement — trouvé par inspection
# du PDF réel du tableau de bord (liste de modules trop longue), pas par les
# tests automatisés (même leçon que pour les chemins de fichiers, prompt 1.3).
_STYLE_CELLULE_CLE_VALEUR = ParagraphStyle("cellule_cle_valeur", parent=_STYLES["Normal"], fontSize=9, leading=11)
_STYLE_CELLULE_LIBRE = ParagraphStyle("cellule_libre", parent=_STYLES["Normal"], fontSize=8, leading=10)
_STYLE_ENTETE_LIBRE = ParagraphStyle(
    "entete_libre", parent=_STYLES["Normal"], fontSize=8, leading=10, fontName="Helvetica-Bold"
)

_STYLE_TABLEAU_CLE_VALEUR = TableStyle(
    [
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("BACKGROUND", (0, 0), (0, -1), colors.whitesmoke),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]
)

_STYLE_TABLEAU_LIBRE = TableStyle(
    [
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ]
)


class DocumentPDF:
    """Construction incrémentale d'un export PDF : `HIRONDELLES IT LAB` +
    titre + référence en en-tête (chapitre 14, cas de test 12), sections
    clé/valeur ou tableaux libres au choix, date et auteur en pied de page
    (règle 3, CLAUDE.md : traçabilité — horodatage et auteur)."""

    def __init__(self, titre: str, reference: str | None = None):
        self.elements = [
            Paragraph("HIRONDELLES IT LAB", _STYLES["Heading2"]),
            Paragraph(titre, _STYLES["Title"]),
        ]
        if reference:
            self.elements.append(Paragraph(f"Référence : {reference}", _STYLES["Normal"]))
        self.elements.append(Spacer(1, 0.5 * cm))

    def paragraphe(self, texte: str, style: str = "Heading3") -> None:
        self.elements.append(Paragraph(texte, _STYLES[style]))

    def section(self, titre: str, lignes: list[tuple[str, object]]) -> None:
        self.elements.append(Paragraph(titre, _STYLES["Heading3"]))
        if lignes:
            donnees = [
                [Paragraph(cle, _STYLE_CELLULE_CLE_VALEUR), Paragraph("—" if valeur is None else str(valeur), _STYLE_CELLULE_CLE_VALEUR)]
                for cle, valeur in lignes
            ]
            table = Table(donnees, colWidths=[6 * cm, 10 * cm])
            table.setStyle(_STYLE_TABLEAU_CLE_VALEUR)
            self.elements.append(table)
        self.elements.append(Spacer(1, 0.4 * cm))

    def tableau(self, titre: str | None, entetes: list[str], lignes: list[list], col_widths: list[float] | None = None) -> None:
        if titre:
            self.elements.append(Paragraph(titre, _STYLES["Heading3"]))
        if lignes:
            donnees = [[Paragraph(e, _STYLE_ENTETE_LIBRE) for e in entetes]] + [
                [Paragraph("—" if v is None else str(v), _STYLE_CELLULE_LIBRE) for v in ligne] for ligne in lignes
            ]
            table = Table(donnees, colWidths=col_widths, repeatRows=1)
            table.setStyle(_STYLE_TABLEAU_LIBRE)
            self.elements.append(table)
        else:
            self.elements.append(Paragraph("Aucune donnée.", _STYLES["Normal"]))
        self.elements.append(Spacer(1, 0.4 * cm))

    def pied_de_page(self, genere_le: str, auteur: str) -> None:
        self.elements.append(Spacer(1, 0.3 * cm))
        self.elements.append(Paragraph(f"Généré le {genere_le} — Auteur : {auteur}", _STYLES["Normal"]))

    def construire(self) -> bytes:
        tampon = io.BytesIO()
        doc = SimpleDocTemplate(tampon, pagesize=A4, topMargin=1.5 * cm, bottomMargin=1.5 * cm)
        doc.build(self.elements)
        return tampon.getvalue()

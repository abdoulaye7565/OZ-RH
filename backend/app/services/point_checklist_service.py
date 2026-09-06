"""Gestion du référentiel de checklists paramétrables (prompt 2.4)."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.enums import TypeInspection
from app.models.point_checklist import PointChecklist
from app.schemas.point_checklist import PointChecklistCreation


def lister_points(db: Session, type_inspection: TypeInspection) -> list[PointChecklist]:
    requete = (
        select(PointChecklist)
        .where(PointChecklist.type_inspection == type_inspection, PointChecklist.archive.is_(False))
        .order_by(PointChecklist.ordre)
    )
    return list(db.scalars(requete))


def creer_point(db: Session, donnees: PointChecklistCreation, cree_par_id: int) -> PointChecklist:
    point = PointChecklist(
        type_inspection=donnees.type_inspection,
        categorie=donnees.categorie,
        ordre=donnees.ordre,
        libelle=donnees.libelle,
        cree_par_id=cree_par_id,
    )
    db.add(point)
    db.commit()
    db.refresh(point)
    return point


def archiver_point(db: Session, point: PointChecklist, modifie_par_id: int) -> PointChecklist:
    """Pas de suppression physique (règle transversale) : les inspections
    passées qui référencent ce point gardent un `point_checklist_id` valide."""
    point.archive = True
    point.modifie_par_id = modifie_par_id
    db.commit()
    db.refresh(point)
    return point

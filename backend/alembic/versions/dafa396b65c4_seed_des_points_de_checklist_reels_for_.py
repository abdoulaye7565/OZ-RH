"""seed des points de checklist reels FOR-SHEQ-005 010 011

Contenu défini dans app/models/checklist_referentiel.py (module partagé avec
les fixtures de test, pour ne jamais dupliquer ces 93 lignes à deux endroits).

Revision ID: dafa396b65c4
Revises: fb8c539876c8
Create Date: 2026-09-06 04:41:12.000000

"""
from datetime import datetime, timezone
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from app.models.checklist_referentiel import lignes_a_semer

# revision identifiers, used by Alembic.
revision: str = 'dafa396b65c4'
down_revision: Union[str, Sequence[str], None] = 'fb8c539876c8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


point_checklist = sa.table(
    "point_checklist",
    sa.column("type_inspection", sa.String),
    sa.column("categorie", sa.String),
    sa.column("ordre", sa.Integer),
    sa.column("libelle", sa.String),
    sa.column("cree_le", sa.DateTime),
    sa.column("modifie_le", sa.DateTime),
    sa.column("archive", sa.Boolean),
)


def upgrade() -> None:
    maintenant = datetime.now(timezone.utc)
    lignes = [
        {**ligne, "cree_le": maintenant, "modifie_le": maintenant, "archive": False}
        for ligne in lignes_a_semer()
    ]
    op.bulk_insert(point_checklist, lignes)


def downgrade() -> None:
    op.execute(point_checklist.delete())

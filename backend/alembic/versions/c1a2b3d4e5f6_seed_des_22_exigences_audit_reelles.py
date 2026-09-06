"""seed des 22 exigences d'audit reelles FOR-SHEQ-017

Contenu défini dans app/models/audit_referentiel.py (module partagé avec les
fixtures de test, pour ne jamais dupliquer ces 22 lignes à deux endroits) —
même principe que dafa396b65c4 pour les points de checklist.

Revision ID: c1a2b3d4e5f6
Revises: b0fef0f9add6
Create Date: 2026-09-06 09:45:00.000000

"""
from datetime import datetime, timezone
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from app.models.audit_referentiel import lignes_a_semer

# revision identifiers, used by Alembic.
revision: str = 'c1a2b3d4e5f6'
down_revision: Union[str, Sequence[str], None] = 'b0fef0f9add6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


exigence_audit = sa.table(
    "exigence_audit",
    sa.column("numero", sa.Integer),
    sa.column("chapitre", sa.String),
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
    op.bulk_insert(exigence_audit, lignes)


def downgrade() -> None:
    op.execute(exigence_audit.delete())

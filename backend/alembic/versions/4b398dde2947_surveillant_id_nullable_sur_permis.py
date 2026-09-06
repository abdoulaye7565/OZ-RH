"""surveillant_id nullable sur permis

Revision ID: 4b398dde2947
Revises: 99cb17e1c898
Create Date: 2026-09-06 01:49:30.365209

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4b398dde2947'
down_revision: Union[str, Sequence[str], None] = '99cb17e1c898'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # batch_alter_table : SQLite ne supporte pas ALTER COLUMN directement (il
    # recrée la table sous le capot) ; op.alter_column seul échouerait au
    # premier `alembic upgrade` sur la base de développement.
    with op.batch_alter_table("permis") as batch_op:
        batch_op.alter_column(
            "surveillant_id",
            existing_type=sa.INTEGER(),
            nullable=True,
        )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("permis") as batch_op:
        batch_op.alter_column(
            "surveillant_id",
            existing_type=sa.INTEGER(),
            nullable=False,
        )

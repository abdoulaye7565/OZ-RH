"""ajout equipement_id sur inspection

Revision ID: 14382e24e575
Revises: dafa396b65c4
Create Date: 2026-09-06 05:28:46.078764

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '14382e24e575'
down_revision: Union[str, Sequence[str], None] = 'dafa396b65c4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # batch_alter_table : SQLite ne supporte pas l'ajout d'une contrainte de
    # clé étrangère nommée via ALTER TABLE (voir 4b398dde2947 et fb8c539876c8
    # pour le même motif sur d'autres migrations de ce projet).
    with op.batch_alter_table("inspection") as batch_op:
        batch_op.add_column(sa.Column('equipement_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            op.f('fk_inspection_equipement_id_equipement'), 'equipement', ['equipement_id'], ['id']
        )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("inspection") as batch_op:
        batch_op.drop_constraint(op.f('fk_inspection_equipement_id_equipement'), type_='foreignkey')
        batch_op.drop_column('equipement_id')

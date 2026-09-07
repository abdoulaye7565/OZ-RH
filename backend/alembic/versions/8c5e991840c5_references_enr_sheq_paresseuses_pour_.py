"""references enr-sheq paresseuses pour export pdf

Revision ID: 8c5e991840c5
Revises: 90df54758db3
Create Date: 2026-09-07 00:36:34.469581

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8c5e991840c5'
down_revision: Union[str, Sequence[str], None] = '90df54758db3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # batch_alter_table : SQLite ne supporte pas l'ajout d'une contrainte
    # UNIQUE nommée via ALTER TABLE (même motif que 14382e24e575 et suivantes).
    with op.batch_alter_table("campagne_audit") as batch_op:
        batch_op.add_column(sa.Column('reference', sa.String(length=20), nullable=True))
        batch_op.create_unique_constraint(op.f('uq_campagne_audit_reference'), ['reference'])
    with op.batch_alter_table("evaluation_slam") as batch_op:
        batch_op.add_column(sa.Column('reference', sa.String(length=20), nullable=True))
        batch_op.create_unique_constraint(op.f('uq_evaluation_slam_reference'), ['reference'])
    with op.batch_alter_table("inspection") as batch_op:
        batch_op.add_column(sa.Column('reference', sa.String(length=20), nullable=True))
        batch_op.create_unique_constraint(op.f('uq_inspection_reference'), ['reference'])
    with op.batch_alter_table("revue_direction") as batch_op:
        batch_op.add_column(sa.Column('reference', sa.String(length=20), nullable=True))
        batch_op.create_unique_constraint(op.f('uq_revue_direction_reference'), ['reference'])


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("revue_direction") as batch_op:
        batch_op.drop_constraint(op.f('uq_revue_direction_reference'), type_='unique')
        batch_op.drop_column('reference')
    with op.batch_alter_table("inspection") as batch_op:
        batch_op.drop_constraint(op.f('uq_inspection_reference'), type_='unique')
        batch_op.drop_column('reference')
    with op.batch_alter_table("evaluation_slam") as batch_op:
        batch_op.drop_constraint(op.f('uq_evaluation_slam_reference'), type_='unique')
        batch_op.drop_column('reference')
    with op.batch_alter_table("campagne_audit") as batch_op:
        batch_op.drop_constraint(op.f('uq_campagne_audit_reference'), type_='unique')
        batch_op.drop_column('reference')

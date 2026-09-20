"""lien evaluation_slam permis

Revision ID: 7901cba3e6ab
Revises: 3197fb535115
Create Date: 2026-09-10 06:40:50.303144

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7901cba3e6ab'
down_revision: Union[str, Sequence[str], None] = '3197fb535115'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Rattache une évaluation SLAM au permis qu'elle justifie (revue
    d'ensemble 2026-09-10). Colonne nullable ; `batch_alter_table` pour que la
    contrainte de clé étrangère passe aussi sous SQLite (stratégie
    copy-and-move), pas seulement PostgreSQL."""
    with op.batch_alter_table("evaluation_slam") as batch:
        batch.add_column(sa.Column("permis_id", sa.Integer(), nullable=True))
        batch.create_foreign_key(
            batch.f("fk_evaluation_slam_permis_id_permis"), "permis", ["permis_id"], ["id"]
        )


def downgrade() -> None:
    with op.batch_alter_table("evaluation_slam") as batch:
        batch.drop_constraint(batch.f("fk_evaluation_slam_permis_id_permis"), type_="foreignkey")
        batch.drop_column("permis_id")

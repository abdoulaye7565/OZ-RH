"""seed des 10 questions de quiz reelles FOR-SHEQ-015

Contenu défini dans app/models/quiz_referentiel.py (module partagé avec les
fixtures de test) — même principe que dafa396b65c4 et c1a2b3d4e5f6.

Revision ID: d2b3c4e5f6a7
Revises: c1a2b3d4e5f6
Create Date: 2026-09-06 09:46:00.000000

"""
from datetime import datetime, timezone
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from app.models.quiz_referentiel import lignes_a_semer

# revision identifiers, used by Alembic.
revision: str = 'd2b3c4e5f6a7'
down_revision: Union[str, Sequence[str], None] = 'c1a2b3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


question_quiz = sa.table(
    "question_quiz",
    sa.column("enonce", sa.String),
    sa.column("choix", sa.JSON),
    sa.column("reponse_correcte", sa.String),
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
    op.bulk_insert(question_quiz, lignes)


def downgrade() -> None:
    op.execute(question_quiz.delete())

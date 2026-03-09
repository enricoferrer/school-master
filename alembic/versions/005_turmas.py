"""Create turmas table

Revision ID: 005_turmas
Revises: 004_professor_disciplinas
Create Date: 2025-01-05 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '005_turmas'
down_revision: Union[str, None] = '004_professor_disciplinas'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'turmas',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('sala', sa.String(), nullable=True),
        sa.Column('serie', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_turmas_id'), 'turmas', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_turmas_id'), table_name='turmas')
    op.drop_table('turmas')

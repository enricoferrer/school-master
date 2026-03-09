"""Create disciplinas table

Revision ID: 003_disciplinas
Revises: 002_professores
Create Date: 2025-01-03 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '003_disciplinas'
down_revision: Union[str, None] = '002_professores'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'disciplinas',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('nome', sa.String(), nullable=False),
        sa.Column('codigo', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('codigo')
    )
    op.create_index(op.f('ix_disciplinas_id'), 'disciplinas', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_disciplinas_id'), table_name='disciplinas')
    op.drop_table('disciplinas')

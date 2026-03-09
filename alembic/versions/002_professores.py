"""Create professores table

Revision ID: 002_professores
Revises: 001_initial
Create Date: 2025-01-02 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '002_professores'
down_revision: Union[str, None] = '001_initial'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'professores',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('fk_funcionario', sa.Uuid(), nullable=False),
        sa.Column('carga_horaria', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['fk_funcionario'], ['funcionarios.id'], ondelete='NO ACTION', onupdate='NO ACTION'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_professores_id'), 'professores', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_professores_id'), table_name='professores')
    op.drop_table('professores')

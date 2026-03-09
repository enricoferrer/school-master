"""Create turma_professores table

Revision ID: 006_turma_professores
Revises: 005_turmas
Create Date: 2025-01-06 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '006_turma_professores'
down_revision: Union[str, None] = '005_turmas'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'turma_professores',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('fk_turma', sa.Uuid(), nullable=False),
        sa.Column('fk_professor', sa.Uuid(), nullable=False),
        sa.Column('fk_disciplina', sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(['fk_turma'], ['turmas.id'], ondelete='NO ACTION', onupdate='NO ACTION'),
        sa.ForeignKeyConstraint(['fk_professor'], ['professores.id'], ondelete='NO ACTION', onupdate='NO ACTION'),
        sa.ForeignKeyConstraint(['fk_disciplina'], ['disciplinas.id'], ondelete='NO ACTION', onupdate='NO ACTION'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_turma_professores_id'), 'turma_professores', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_turma_professores_id'), table_name='turma_professores')
    op.drop_table('turma_professores')

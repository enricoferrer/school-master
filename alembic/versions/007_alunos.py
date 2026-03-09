"""Create alunos table

Revision ID: 007_alunos
Revises: 006_turma_professores
Create Date: 2025-01-07 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '007_alunos'
down_revision: Union[str, None] = '006_turma_professores'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'alunos',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('fk_turma', sa.Uuid(), nullable=True),
        sa.Column('fk_usuario', sa.Uuid(), nullable=False),
        sa.Column('matricula', sa.String(), nullable=False),
        sa.Column('data_matricula', sa.Date(), nullable=False),
        sa.ForeignKeyConstraint(['fk_turma'], ['turmas.id'], ondelete='NO ACTION', onupdate='NO ACTION'),
        sa.ForeignKeyConstraint(['fk_usuario'], ['usuarios.id'], ondelete='NO ACTION', onupdate='NO ACTION'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_alunos_id'), 'alunos', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_alunos_id'), table_name='alunos')
    op.drop_table('alunos')

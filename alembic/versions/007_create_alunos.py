"""Create alunos table

Revision ID: 007_create_alunos
Revises: 006_create_turma_professores
Create Date: 2026-03-19 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '007_create_alunos'
down_revision: Union[str, None] = '006_create_turma_professores'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create alunos table
    op.create_table(
        'alunos',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('matricula', sa.String(), nullable=False),
        sa.Column('data_matricula', sa.Date(), nullable=False),
        sa.Column('fk_turma', sa.Uuid(), nullable=True),
        sa.Column('fk_usuario', sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(['fk_turma'], ['turmas.id'], ondelete='NO ACTION', onupdate='NO ACTION'),
        sa.ForeignKeyConstraint(['fk_usuario'], ['usuarios.id'], ondelete='NO ACTION', onupdate='NO ACTION'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('matricula')
    )
    op.create_index(op.f('ix_alunos_id'), 'alunos', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_alunos_id'), table_name='alunos')
    op.drop_table('alunos')

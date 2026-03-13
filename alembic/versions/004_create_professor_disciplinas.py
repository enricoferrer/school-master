"""Create professor_disciplinas table

Revision ID: 004_create_professor_disciplinas
Revises: 003_create_disciplinas
Create Date: 2026-03-13 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '004_create_professor_disciplinas'
down_revision: Union[str, None] = '003_create_disciplinas'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create professor_disciplinas table
    op.create_table(
        'professor_disciplinas',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('fk_professor', sa.Uuid(), nullable=False),
        sa.Column('fk_disciplina', sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(['fk_professor'], ['professores.id'], ondelete='NO ACTION', onupdate='NO ACTION'),
        sa.ForeignKeyConstraint(['fk_disciplina'], ['disciplinas.id'], ondelete='NO ACTION', onupdate='NO ACTION'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_professor_disciplinas_id'), 'professor_disciplinas', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_professor_disciplinas_id'), table_name='professor_disciplinas')
    op.drop_table('professor_disciplinas')

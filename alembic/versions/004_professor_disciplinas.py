"""Create professor_disciplinas table

Revision ID: 004_professor_disciplinas
Revises: 003_disciplinas
Create Date: 2025-01-04 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '004_professor_disciplinas'
down_revision: Union[str, None] = '003_disciplinas'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
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

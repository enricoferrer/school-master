"""Create roles table

Revision ID: 008_create_roles
Revises: 007_create_alunos
Create Date: 2026-03-20 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '008_create_roles'
down_revision: Union[str, None] = '007_create_alunos'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Create roles table
    op.create_table(
        'roles',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('nome', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('nome')
    )
    op.create_index(op.f('ix_roles_id'), 'roles', ['id'], unique=False)
    op.add_column("usuarios", sa.Column('fk_role', sa.Uuid(), sa.ForeignKey("roles.id"), nullable=False))


def downgrade() -> None:
    op.drop_index(op.f('ix_roles_id'), table_name='roles')
    op.drop_column("usuarios", "fk_role")
    op.drop_table('roles')
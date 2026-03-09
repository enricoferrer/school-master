"""Initial migration - Create usuarios and funcionarios tables

Revision ID: 001_initial
Revises: 
Create Date: 2025-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create usuarios table
    op.create_table(
        'usuarios',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('nome_completo', sa.String(), nullable=False),
        sa.Column('nome_social', sa.String(), nullable=True),
        sa.Column('data_nascimento', sa.Date(), nullable=False),
        sa.Column('cpf', sa.String(), nullable=False),
        sa.Column('registro_geral', sa.String(), nullable=False),
        sa.Column('genero', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('telefone', sa.String(), nullable=True),
        sa.Column('endereco', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('cpf'),
        sa.UniqueConstraint('registro_geral')
    )
    op.create_index(op.f('ix_usuarios_id'), 'usuarios', ['id'], unique=False)

    # Create funcionarios table
    op.create_table(
        'funcionarios',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('fk_usuario', sa.Uuid(), nullable=False),
        sa.Column('data_admissao', sa.Date(), nullable=False),
        sa.Column('matricula', sa.String(), nullable=False),
        sa.Column('cargo', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['fk_usuario'], ['usuarios.id'], ondelete='NO ACTION', onupdate='NO ACTION'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_funcionarios_id'), 'funcionarios', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_funcionarios_id'), table_name='funcionarios')
    op.drop_table('funcionarios')
    op.drop_index(op.f('ix_usuarios_id'), table_name='usuarios')
    op.drop_table('usuarios')

"""Create roles table

Revision ID: 009_updt_user_crt_audit_logs
Revises: 008_create_roles
Create Date: 2026-03-20 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid


# revision identifiers, used by Alembic.
revision: str = '009_updt_user_crt_audit_logs'
down_revision: Union[str, None] = '008_create_roles'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Colunas novas na tabela usuarios
    op.add_column('usuarios', sa.Column('senha_hash', sa.String(), nullable=True))
    op.add_column('usuarios', sa.Column('tentativas_falhas', sa.Integer(), server_default='0'))
    op.add_column('usuarios', sa.Column('bloqueado_ate', sa.DateTime(timezone=True), nullable=True))
    op.add_column('usuarios', sa.Column('is_active', sa.Boolean(), server_default='true'))
    op.add_column('usuarios', sa.Column('criado_em', sa.DateTime(timezone=True), server_default=sa.func.now()))
    op.add_column('usuarios', sa.Column('atualizado_em', sa.DateTime(timezone=True), server_default=sa.func.now()))

    # Tabela audit_logs
    op.create_table(
        'audit_logs',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('fk_usuario', UUID(as_uuid=True), sa.ForeignKey('usuarios.id', ondelete='SET NULL'), nullable=True),
        sa.Column('operacao', sa.String(), nullable=False),
        sa.Column('tabela_afetada', sa.String(), nullable=False),
        sa.Column('registro_id', UUID(as_uuid=True), nullable=True),
        sa.Column('dados_anteriores', JSONB, nullable=True),
        sa.Column('dados_posteriores', JSONB, nullable=True),
        sa.Column('ip_origem', sa.String(), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

def downgrade():
    op.drop_table('audit_logs')
    for col in ['senha_hash', 'fk_role', 'tentativas_falhas', 'bloqueado_ate', 'is_active', 'criado_em', 'atualizado_em']:
        op.drop_column('usuarios', col)
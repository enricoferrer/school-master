"""cria tabela notificacoes

Revision ID: 019_create_notificacoes
Revises: 018_add_ano_letivo_turma
Create Date: 2026-03-30 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


revision: str = "019_create_notificacoes"
down_revision: Union[str, None] = "018_add_ano_letivo_turma"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "notificacoes",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("fk_usuario_destino", UUID(as_uuid=True), nullable=False),
        sa.Column("tipo", sa.String(), nullable=True),
        sa.Column("titulo", sa.String(), nullable=True),
        sa.Column("mensagem", sa.Text(), nullable=True),
        sa.Column("status", sa.String(), nullable=False, server_default="PENDENTE"),
        sa.Column("criado_em", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP")),
    )


def downgrade() -> None:
    op.drop_table("notificacoes")
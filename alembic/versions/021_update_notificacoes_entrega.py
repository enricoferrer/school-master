"""adiciona colunas de entrega em notificacoes

Revision ID: 021_update_notificacoes_entrega
Revises: 020_add_tipo_responsavel
Create Date: 2026-03-30 00:02:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "021_update_notificacoes_entrega"
down_revision: Union[str, None] = "020_add_tipo_responsavel"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("notificacoes", sa.Column("canal", sa.String(20), nullable=True))
    op.add_column("notificacoes", sa.Column("tentativas", sa.Integer(), server_default="0"))
    op.add_column("notificacoes", sa.Column("enviado_em", sa.DateTime(timezone=True), nullable=True))
    op.add_column("notificacoes", sa.Column("erro_detalhe", sa.Text(), nullable=True))

    op.create_check_constraint(
        "ck_notificacoes_status",
        "notificacoes",
        "status IN ('PENDENTE', 'ENVIADO', 'ENTREGUE', 'FALHOU')",
    )


def downgrade() -> None:
    op.drop_constraint("ck_notificacoes_status", "notificacoes", type_="check")
    op.drop_column("notificacoes", "erro_detalhe")
    op.drop_column("notificacoes", "enviado_em")
    op.drop_column("notificacoes", "tentativas")
    op.drop_column("notificacoes", "canal")
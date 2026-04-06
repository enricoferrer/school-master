"""cria tabela notificacao_preferencias e indices

Revision ID: 022_notif_pref
Revises: 021_update_notificacoes_entrega
Create Date: 2026-03-30 00:03:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


revision: str = "022_notif_pref"
down_revision: Union[str, None] = "021_update_notificacoes_entrega"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "notificacao_preferencias",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("fk_usuario", UUID(as_uuid=True), sa.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False),
        sa.Column("canal", sa.String(20), nullable=False, server_default="EMAIL"),
        sa.Column("tipo_evento", sa.String(50), nullable=False),
        sa.Column("ativo", sa.Boolean(), server_default="true"),
        sa.Column("horario_inicio", sa.Time(), nullable=True),
        sa.Column("horario_fim", sa.Time(), nullable=True),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
    )

    op.create_unique_constraint(
        "uq_preferencia_usuario_canal_evento",
        "notificacao_preferencias",
        ["fk_usuario", "canal", "tipo_evento"],
    )

    # índices
    op.create_index("ix_notificacoes_fk_usuario_destino", "notificacoes", ["fk_usuario_destino"])
    op.create_index("ix_notificacoes_status", "notificacoes", ["status"])
    op.create_index("ix_preferencias_usuario", "notificacao_preferencias", ["fk_usuario"])


def downgrade() -> None:
    op.drop_index("ix_preferencias_usuario", table_name="notificacao_preferencias")
    op.drop_index("ix_notificacoes_status", table_name="notificacoes")
    op.drop_index("ix_notificacoes_fk_usuario_destino", table_name="notificacoes")
    op.drop_table("notificacao_preferencias")
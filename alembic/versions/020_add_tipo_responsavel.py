"""adiciona tipo_responsavel em aluno_responsaveis

Revision ID: 020_add_tipo_responsavel
Revises: 019_create_notificacoes
Create Date: 2026-03-30 00:01:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "020_add_tipo_responsavel"
down_revision: Union[str, None] = "019_create_notificacoes"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "aluno_responsaveis",
        sa.Column(
            "tipo_responsavel",
            sa.String(20),
            nullable=False,
            server_default="PRIMARIO",
        ),
    )

    op.create_check_constraint(
        "ck_aluno_responsaveis_tipo",
        "aluno_responsaveis",
        "tipo_responsavel IN ('PRIMARIO', 'SECUNDARIO')",
    )


def downgrade() -> None:
    op.drop_constraint("ck_aluno_responsaveis_tipo", "aluno_responsaveis", type_="check")
    op.drop_column("aluno_responsaveis", "tipo_responsavel")
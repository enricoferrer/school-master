"""adiciona coluna ano_letivo à tabela turmas

Revision ID: 018_add_ano_letivo_turma
Revises: 017_avaliacoes_periodo_indexes
Create Date: 2026-03-24 00:00:00.000000
"""
from datetime import date
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '018_add_ano_letivo_turma'
down_revision: Union[str, None] = '017_avaliacoes_periodo_indexes'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.add_column(
        "turmas",
        sa.Column(
            "ano_letivo",
            sa.String(4),
            nullable=False,
            server_default=date.today().strftime("%Y"),   
        ),
    )
    
def downgrade() -> None:
    op.drop_column("turmas", "ano_letivo")
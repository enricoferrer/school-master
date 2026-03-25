# migrations/versions/xxxx_avaliacoes_periodo_e_indexes.py
"""notas: adiciona periodo em avaliacoes e indices de performance

Revision ID: 017_avaliacoes_periodo_indexes
Revises: 016_create_notas
Create Date: 2026-03-24 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '017_avaliacoes_periodo_indexes'
down_revision: Union[str, None] = '016_create_notas'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

PERIODOS_VALIDOS = ("1B", "2B", "3B", "4B")


def upgrade() -> None:
    op.add_column(
        "avaliacoes",
        sa.Column(
            "periodo",
            sa.String(2),
            nullable=False,
            server_default="1B",   
        ),
    )

    op.create_check_constraint(
        "ck_avaliacoes_periodo",
        "avaliacoes",
        "periodo IN ('1B', '2B', '3B', '4B')",
    )

    op.create_index(
        "ix_notas_aluno_avaliacao",
        "notas",
        ["fk_aluno", "fk_avaliacao"],
        unique=True, 
    )

    op.create_index(
        "ix_avaliacoes_turma_professor_periodo",
        "avaliacoes",
        ["fk_turma_professor", "periodo"],
    )


def downgrade() -> None:
    op.drop_index("ix_avaliacoes_turma_professor_periodo", table_name="avaliacoes")
    op.drop_index("ix_notas_aluno_avaliacao",              table_name="notas")
    op.drop_constraint("ck_avaliacoes_periodo",            "avaliacoes", type_="check")
    op.drop_column("avaliacoes", "periodo")
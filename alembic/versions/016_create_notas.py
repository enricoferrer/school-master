"""cria tabela notas

Revision ID: 016_create_notas
Revises: 015_create_avaliacoes
Create Date: 2026-03-24 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '016_create_notas'
down_revision: Union[str, None] = '015_create_avaliacoes'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "notas",
        sa.Column("id", sa.UUID(), primary_key=True, server_default=sa.text("gen_random_uuid()")),

        sa.Column("fk_aluno", sa.UUID(), nullable=False),
        sa.Column("fk_avaliacao", sa.UUID(), nullable=False),

        sa.Column("valor", sa.Numeric(), nullable=True),

        sa.Column(
            "data_lancamento",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),

        sa.ForeignKeyConstraint(
            ["fk_aluno"],
            ["alunos.id"],
            ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["fk_avaliacao"],
            ["avaliacoes.id"],
            ondelete="CASCADE"
        ),
    )

    op.create_index(
        "ix_notas_fk_avaliacao",
        "notas",
        ["fk_avaliacao"],
    )


def downgrade() -> None:
    op.drop_index("ix_notas_fk_avaliacao", table_name="notas")
    op.drop_table("notas")
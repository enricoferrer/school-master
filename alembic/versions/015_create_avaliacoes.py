"""cria tabela avaliacoes
Revision ID: 015_create_avaliacoes
Revises: 014_create_aluno_responsaveis
Create Date: 2026-03-24 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '015_create_avaliacoes'
down_revision: Union[str, None] = '014_create_aluno_responsaveis'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "avaliacoes",
        sa.Column("id", sa.UUID(), primary_key=True, server_default=sa.text("gen_random_uuid()")),

        sa.Column("fk_turma_professor", sa.UUID(), nullable=False),

        sa.Column("titulo", sa.String(), nullable=False),
        sa.Column("tipo", sa.String(), nullable=True),

        sa.Column("peso", sa.Numeric(), nullable=False, server_default="1.0"),
        sa.Column("data_aplicacao", sa.Date(), nullable=True),

        sa.ForeignKeyConstraint(
            ["fk_turma_professor"],
            ["turma_professores.id"],
            ondelete="CASCADE"
        ),
    )

    op.create_index(
        "ix_avaliacoes_fk_turma_professor",
        "avaliacoes",
        ["fk_turma_professor"],
    )


def downgrade() -> None:
    op.drop_index("ix_avaliacoes_fk_turma_professor", table_name="avaliacoes")
    op.drop_table("avaliacoes")
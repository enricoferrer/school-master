"""create aluno_responsaveis table

Revision ID: 014_create_aluno_responsaveis
Revises: 013_create_frequencias
Create Date: 2026-03-24 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '014_create_aluno_responsaveis'
down_revision: Union[str, None] = '013_create_frequencias'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "aluno_responsaveis",
        sa.Column(
            "fk_aluno",
            sa.UUID,
            sa.ForeignKey("alunos.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "fk_responsavel",
            sa.UUID,
            sa.ForeignKey("usuarios.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("parentesco", sa.String, nullable=True),
        sa.Column(
            "is_financeiro",
            sa.Boolean,
            nullable=False,
            server_default=sa.text("false"),
        ),
    )

    op.create_index(
        "ix_aluno_responsaveis_responsavel",
        "aluno_responsaveis",
        ["fk_responsavel"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_aluno_responsaveis_responsavel",
        table_name="aluno_responsaveis",
    )
    op.drop_table("aluno_responsaveis")
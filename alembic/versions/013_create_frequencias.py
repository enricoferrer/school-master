"""create frequencias table

Revision ID: 013_create_frequencias
Revises: 012_seed_admin_user
Create Date: 2026-03-24 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '013_create_frequencias'
down_revision: Union[str, None] = '012_seed_admin_user'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

    op.create_table(
        "frequencias",
        sa.Column(
            "id",
            sa.UUID,
            primary_key=True,
            server_default=sa.text("gen_random_uuid()")
        ),
        sa.Column(
            "fk_aluno",
            sa.UUID,
            sa.ForeignKey("alunos.id", ondelete="CASCADE"),
            nullable=False
        ),
        sa.Column(
            "fk_turma_professor",
            sa.UUID,
            sa.ForeignKey("turma_professores.id", ondelete="CASCADE"),
            nullable=False
        ),
        sa.Column("data", sa.Date, nullable=False),
        sa.Column(
            "presenca",
            sa.Boolean,
            nullable=False,
            server_default=sa.text("true")
        ),
        sa.Column(
            "metodo_registro",
            sa.String,
            nullable=False,
            server_default=sa.text("'MANUAL'")
        ),

        sa.UniqueConstraint(
            "fk_aluno",
            "fk_turma_professor",
            "data",
            name="uq_frequencia_aluno_turma_data",
        ),
    )

    op.create_index(
        "ix_frequencias_aluno_turma_professor_data",
        "frequencias",
        ["fk_aluno", "fk_turma_professor", "data"],
        unique=True,
    )

    op.create_index(
        "ix_frequencias_turma_professor_data",
        "frequencias",
        ["fk_turma_professor", "data"],
    )

    op.create_index(
        "ix_frequencias_aluno_presenca",
        "frequencias",
        ["fk_aluno", "presenca"],
    )


def downgrade() -> None:
    op.drop_index("ix_frequencias_aluno_presenca", table_name="frequencias")
    op.drop_index("ix_frequencias_turma_professor_data", table_name="frequencias")
    op.drop_index("ix_frequencias_aluno_turma_professor_data", table_name="frequencias")

    op.drop_table("frequencias")
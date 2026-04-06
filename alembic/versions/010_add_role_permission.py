"""add role_permissions table and seed data

Revision ID: 010_add_role_permission
Revises: 009_updt_user_crt_audit_logs
Create Date: 2026-03-21 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '010_add_role_permission'
down_revision: Union[str, None] = '009_updt_user_crt_audit_logs'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Mapeamento de papéis → permissões
_ROLE_PERMISSIONS = {
    "ADMIN": [
        "user:read","user:write","user:delete",
        "role:assign","role:revoke",
        "aluno:read","aluno:write",
        "grade:read","grade:write",
        "frequencia:read","frequencia:write",
        "financeiro:read","financeiro:write",
        "report:read","report:generate",
        "calendario:read","calendario:write",
        "notificacao:read","notificacao:write",
        "funcionario:read","funcionario:write",
        "analytics:read","analytics:write",
        "audit:read", "portal:read",
    ],
    "DIRETOR": [
        "user:read","aluno:read","grade:read","frequencia:read",
        "financeiro:read","report:read","report:generate",
        "calendario:read","calendario:write",
        "notificacao:read","notificacao:write","funcionario:read",
        "analytics:read", "portal:read",
    ],
    "PROFESSOR": [
        "aluno:read","grade:read","grade:write",
        "frequencia:read","frequencia:write",
        "calendario:read","notificacao:read",
        "portal:read",
    ],
    "RESPONSAVEL": [
        "aluno:read","grade:read","frequencia:read",
        "financeiro:read","calendario:read","notificacao:read",
        "portal:read",
    ],
    "ALUNO": [
        "grade:read","frequencia:read","calendario:read","notificacao:read",
        "portal:read",
    ],
}


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

    # Cria tabela role_permissions
    op.create_table(
        "role_permissions",
        sa.Column("id", sa.UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "fk_role",
            sa.UUID,
            sa.ForeignKey("roles.id", ondelete="CASCADE"),
            nullable=False,
            index=True
        ),
        sa.Column("permission", sa.String(100), nullable=False),
        sa.UniqueConstraint("fk_role", "permission", name="uq_role_permission"),
    )

    conn = op.get_bind()

    for role_nome, permissions in _ROLE_PERMISSIONS.items():
        # Tenta buscar role existente
        result = conn.execute(
            sa.text("SELECT id FROM roles WHERE nome = :nome"),
            {"nome": role_nome},
        ).fetchone()

        if result:
            role_id = result[0]
        else:
            # Insere role com UUID gerado no banco (idempotente)
            insert_result = conn.execute(
                sa.text(
                    """
                    INSERT INTO roles (id, nome)
                    VALUES (gen_random_uuid(), :nome)
                    ON CONFLICT (nome) DO NOTHING
                    RETURNING id
                    """
                ),
                {"nome": role_nome},
            ).fetchone()

            if insert_result:
                role_id = insert_result[0]
            else:
                # fallback caso já exista (por causa do ON CONFLICT)
                role_id = conn.execute(
                    sa.text("SELECT id FROM roles WHERE nome = :nome"),
                    {"nome": role_nome},
                ).fetchone()[0]

        # Insere permissões
        for perm in permissions:
            conn.execute(
                sa.text(
                    """
                    INSERT INTO role_permissions (fk_role, permission)
                    VALUES (:role_id, :perm)
                    ON CONFLICT ON CONSTRAINT uq_role_permission DO NOTHING
                    """
                ),
                {"role_id": role_id, "perm": perm},
            )


def downgrade() -> None:
    op.drop_table("role_permissions")
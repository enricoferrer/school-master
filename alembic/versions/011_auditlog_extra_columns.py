
"""audit: add immutability triggers and extra columns

Revision ID: 011_auditlog_extra_columns
Revises: 010_add_role_permission
Create Date: 2026-03-23 00:00:00.000000
"""
from typing import Sequence

from alembic import op
from alembic.environment import Union
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision: str = "011_auditlog_extra_columns"
down_revision: Union[str, None] = '010_add_role_permission'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade() -> None:
    op.add_column("audit_logs", sa.Column("role_usuario", sa.String(), nullable=True))
    op.add_column("audit_logs", sa.Column("metodo_http",  sa.String(10), nullable=True))
    op.add_column("audit_logs", sa.Column("status_http",  sa.Integer(), nullable=True))
    op.add_column("audit_logs", sa.Column("endpoint",     sa.String(), nullable=True))

    op.execute("""
        CREATE OR REPLACE FUNCTION fn_audit_logs_immutable()
        RETURNS TRIGGER AS $$
        BEGIN
            RAISE EXCEPTION
                'audit_logs é imutável — operação % não permitida', TG_OP
                USING ERRCODE = 'restrict_violation';
            RETURN NULL;
        END;
        $$ LANGUAGE plpgsql;
    """)

    op.execute("""
        CREATE TRIGGER trg_audit_no_update
        BEFORE UPDATE ON audit_logs
        FOR EACH ROW EXECUTE FUNCTION fn_audit_logs_immutable();
    """)

    op.execute("""
        CREATE TRIGGER trg_audit_no_delete
        BEFORE DELETE ON audit_logs
        FOR EACH ROW EXECUTE FUNCTION fn_audit_logs_immutable();
    """)

    op.create_index("ix_audit_logs_fk_usuario",    "audit_logs", ["fk_usuario"])
    op.create_index("ix_audit_logs_timestamp",     "audit_logs", ["timestamp"])
    op.create_index("ix_audit_logs_tabela_operacao","audit_logs", ["tabela_afetada", "operacao"])


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_audit_no_delete ON audit_logs;")
    op.execute("DROP TRIGGER IF EXISTS trg_audit_no_update ON audit_logs;")
    op.execute("DROP FUNCTION IF EXISTS fn_audit_logs_immutable;")

    op.drop_index("ix_audit_logs_tabela_operacao", table_name="audit_logs")
    op.drop_index("ix_audit_logs_timestamp",       table_name="audit_logs")
    op.drop_index("ix_audit_logs_fk_usuario",      table_name="audit_logs")

    op.drop_column("audit_logs", "endpoint")
    op.drop_column("audit_logs", "status_http")
    op.drop_column("audit_logs", "metodo_http")
    op.drop_column("audit_logs", "role_usuario")
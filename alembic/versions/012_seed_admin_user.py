"""seed: cria usuário administrador do sistema

Revision ID: 012_seed_admin_user
Revises: 011_auditlog_extra_columns
Create Date: 2026-03-23 00:00:00.000000
"""
from typing import Sequence

from alembic import op
from alembic.environment import Union
from sqlalchemy.sql import text
from passlib.context import CryptContext
import uuid

revision: str = "012_seed_admin_user"
down_revision: Union[str, None] = '011_auditlog_extra_columns'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ADMIN_ID       = str(uuid.uuid4())
ADMIN_EMAIL    = "admin@schoolmaster.com"
ADMIN_SENHA    = "Admin@1234!"
ADMIN_GENERO   = "MAS"     
ADMIN_CPF      = "00000000000"
ADMIN_ENDERECO = "ENDERECO_ADMIN"
ADMIN_REGISTRO_GERAL = "000000000"
ADMIN_NOME     = "Administrador do Sistema"
ADMIN_NASCIMENTO = "1990-01-01"


def upgrade() -> None:
    conn = op.get_bind()

    role = conn.execute(
        text("SELECT id FROM roles WHERE nome = 'ADMIN' LIMIT 1")
    ).fetchone()

    if role is None:
        raise RuntimeError(
            "Role 'ADMIN' não encontrado. "
            "Rode primeiro a migration que cria os roles."
        )

    role_id = str(role[0])

    ja_existe = conn.execute(
        text("SELECT id FROM usuarios WHERE email = :email"),
        {"email": ADMIN_EMAIL},
    ).fetchone()

    if ja_existe:
        print(f"⚠️  Usuário admin já existe ({ADMIN_EMAIL}), pulando seed.")
        return

    senha_hash = _pwd_context.hash(ADMIN_SENHA)

    conn.execute(
        text("""
            INSERT INTO usuarios (
                id, fk_role, nome_completo, email, senha_hash,
                cpf,registro_geral, genero, endereco, data_nascimento, is_active,
                tentativas_falhas, criado_em, atualizado_em
            ) VALUES (
                :id, :fk_role, :nome_completo, :email, :senha_hash,
                :cpf, :registro_geral, :genero, :endereco, :data_nascimento, true,
                0, NOW(), NOW()
            )
        """),
        {
            "id":              ADMIN_ID,
            "fk_role":         role_id,
            "nome_completo":   ADMIN_NOME,
            "email":           ADMIN_EMAIL,
            "senha_hash":      senha_hash,
            "cpf":             ADMIN_CPF,
            "registro_geral":  ADMIN_REGISTRO_GERAL,
            "genero":          ADMIN_GENERO,
            "endereco":        ADMIN_ENDERECO,
            "data_nascimento": ADMIN_NASCIMENTO,
        },
    )

    print(f"✅ Usuário admin criado com sucesso!")
    print(f"   Email : {ADMIN_EMAIL}")
    print(f"   Senha : {ADMIN_SENHA}  ← altere imediatamente em produção")


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        text("DELETE FROM usuarios WHERE email = :email"),
        {"email": ADMIN_EMAIL},
    )
    print(f"🗑️  Usuário admin removido ({ADMIN_EMAIL})")
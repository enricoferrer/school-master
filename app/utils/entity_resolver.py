# utils/entity_resolver.py
"""
Mapeia padrões de endpoint → (Model, nome_da_tabela).
Usado pelo middleware para buscar o estado ANTERIOR de um registro
em operações PUT, PATCH e DELETE.

Adicione novas entidades conforme novas USs forem codadas.
"""
import re
from typing import Type
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, inspect

from app.models.usuario   import Usuario
from app.models.funcionario import Funcionario
from app.models.professor import Professor
from app.models.aluno     import Aluno
from app.models.turma     import Turma
from app.models.disciplina import Disciplina
from app.models.audit_log import AuditLog

# (path_pattern, Model, tabela)
_REGISTRY: list[tuple[re.Pattern, Type, str]] = [
    (re.compile(r"^/usuarios/([^/]+)"),     Usuario,     "usuarios"),
    (re.compile(r"^/funcionarios/([^/]+)"), Funcionario, "funcionarios"),
    (re.compile(r"^/professores/([^/]+)"),  Professor,   "professores"),
    (re.compile(r"^/alunos/([^/]+)"),       Aluno,       "alunos"),
    (re.compile(r"^/turmas/([^/]+)"),       Turma,       "turmas"),
    (re.compile(r"^/disciplinas/([^/]+)"),  Disciplina,  "disciplinas"),
]


def resolve_entity(path: str) -> tuple[Type | None, str | None, str | None]:
    """
    Retorna (Model, tabela, registro_id) a partir do path da request.
    Se não encontrar correspondência, retorna (None, None, None).
    """
    for pattern, model, tabela in _REGISTRY:
        m = pattern.match(path)
        if m:
            return model, tabela, m.group(1)
    return None, None, None


def _model_to_dict(instance) -> dict:
    """Converte um SQLAlchemy model instance em dict serializável."""
    mapper = inspect(type(instance))
    return {
        col.key: getattr(instance, col.key)
        for col in mapper.mapper.column_attrs
    }


async def fetch_before_state(
    db: AsyncSession,
    model: Type,
    registro_id: str,
) -> dict | None:
    """Busca o estado atual de um registro no banco (antes da operação)."""
    try:
        result = await db.execute(select(model).where(model.id == registro_id))
        instance = result.scalar_one_or_none()
        if instance is None:
            return None
        return _model_to_dict(instance)
    except Exception:
        return None
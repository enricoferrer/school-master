from enum import Enum
from typing import Dict, Set


class Permission(str, Enum):
    # Usuários
    USER_READ       = "user:read"
    USER_WRITE      = "user:write"
    USER_DELETE     = "user:delete"

    # Controle de acesso (só ADMIN)
    ROLE_ASSIGN     = "role:assign"
    ROLE_REVOKE     = "role:revoke"

    # Alunos
    ALUNO_READ      = "aluno:read"
    ALUNO_WRITE     = "aluno:write"

    # Notas (row-level por turma para PROFESSOR)
    GRADE_READ      = "grade:read"
    GRADE_WRITE     = "grade:write"

    # Frequência
    FREQUENCIA_READ  = "frequencia:read"
    FREQUENCIA_WRITE = "frequencia:write"

    # Financeiro (PROFESSOR nunca tem isso)
    FINANCEIRO_READ  = "financeiro:read"
    FINANCEIRO_WRITE = "financeiro:write"

    # Relatórios
    REPORT_READ      = "report:read"
    REPORT_GENERATE  = "report:generate"

    # Calendário
    CALENDARIO_READ  = "calendario:read"
    CALENDARIO_WRITE = "calendario:write"

    # Notificações
    NOTIFICACAO_READ  = "notificacao:read"
    NOTIFICACAO_WRITE = "notificacao:write"

    # Funcionários
    FUNCIONARIO_READ  = "funcionario:read"
    FUNCIONARIO_WRITE = "funcionario:write"


# Mapeamento papel → conjunto de permissões
# Esta estrutura é semeada no banco em startup e cacheada no Redis
ROLE_PERMISSIONS: Dict[str, Set[str]] = {
    "ADMIN": {p.value for p in Permission},  # tudo

    "DIRETOR": {
        Permission.USER_READ,
        Permission.ALUNO_READ,
        Permission.GRADE_READ,
        Permission.FREQUENCIA_READ,
        Permission.FINANCEIRO_READ,
        Permission.REPORT_READ,
        Permission.REPORT_GENERATE,
        Permission.CALENDARIO_READ,
        Permission.CALENDARIO_WRITE,
        Permission.NOTIFICACAO_READ,
        Permission.NOTIFICACAO_WRITE,
        Permission.FUNCIONARIO_READ,
    },

    "PROFESSOR": {
        # SEM financeiro:read/write — regra explícita da US-002
        Permission.ALUNO_READ,          # row-level: apenas alunos da sua turma
        Permission.GRADE_READ,          # row-level: apenas notas da sua turma
        Permission.GRADE_WRITE,
        Permission.FREQUENCIA_READ,
        Permission.FREQUENCIA_WRITE,
        Permission.CALENDARIO_READ,
        Permission.NOTIFICACAO_READ,
    },

    "RESPONSAVEL": {
        Permission.ALUNO_READ,          # row-level: apenas seus filhos
        Permission.GRADE_READ,
        Permission.FREQUENCIA_READ,
        Permission.FINANCEIRO_READ,     # row-level: apenas suas faturas
        Permission.CALENDARIO_READ,
        Permission.NOTIFICACAO_READ,
    },

    "ALUNO": {
        Permission.GRADE_READ,          # row-level: apenas suas notas
        Permission.FREQUENCIA_READ,
        Permission.CALENDARIO_READ,
        Permission.NOTIFICACAO_READ,
    },
}

# Papéis válidos para validação de input
VALID_ROLES = set(ROLE_PERMISSIONS.keys())
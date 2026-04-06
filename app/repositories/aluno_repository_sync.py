"""
Repositório síncrono para Aluno.
Usado exclusivamente por tasks Celery (não usa AsyncSession).

⚠️  IMPORTANTE: Este repositório é SÍNCRONO e deve ser usado com SessionLocal (sync),
não com AsyncSessionLocal. Para FastAPI, use AlunoRepository (async).
"""
from uuid import UUID

from sqlalchemy.orm import Session, joinedload

from app.models.aluno import Aluno
from app.schemas.aluno import AlunoCreate, AlunoUpdate


class AlunoRepositorySync:
    """Repositório síncrono para operações de aluno em Celery."""

    def __init__(self, db: Session):
        """
        Args:
            db: Sessão SÍNCRONA do SQLAlchemy (SessionLocal, não AsyncSessionLocal)
        """
        self.db = db

    def _base_query(self):
        """Query base com eager loading de relacionamentos."""
        return self.db.query(Aluno).options(
            joinedload(Aluno.turma),
            joinedload(Aluno.usuario)
        )

    def criar(self, data: AlunoCreate) -> Aluno:
        """Cria um novo aluno (síncrono)."""
        aluno = Aluno(**data.model_dump())
        self.db.add(aluno)
        self.db.commit()
        self.db.refresh(aluno)
        return self._base_query().filter(Aluno.id == aluno.id).first()

    def listar_alunos(self) -> list[Aluno]:
        """Lista todos os alunos (síncrono)."""
        return self._base_query().all()

    def buscar_por_id(self, id: UUID) -> Aluno | None:
        """Busca um aluno por ID (síncrono)."""
        return self._base_query().filter(Aluno.id == id).first()

    def deletar(self, aluno: Aluno) -> None:
        """Deleta um aluno (síncrono)."""
        self.db.delete(aluno)
        self.db.commit()

    def buscar_por_matricula(self, matricula: str) -> Aluno | None:
        """Busca um aluno por matrícula (síncrono)."""
        return self._base_query().filter(Aluno.matricula == matricula).first()

    def atualizar_turma(self, data: AlunoUpdate) -> Aluno | None:
        """Atualiza a turma de um aluno (síncrono)."""
        aluno = self.buscar_por_id(data.id)
        if not aluno:
            return None

        aluno.fk_turma = data.fk_turma
        self.db.commit()
        self.db.refresh(aluno)

        # Reload com relationships
        return self._base_query().filter(Aluno.id == aluno.id).first()

    def buscar_por_turma(self, turma_id: UUID) -> list[Aluno]:
        """Lista todos os alunos de uma turma (síncrono)."""
        return self._base_query().filter(Aluno.fk_turma == turma_id).all()

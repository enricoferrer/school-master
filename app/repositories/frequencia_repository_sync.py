"""
Repositório síncrono para Frequência.
Usado exclusivamente por tasks Celery (não usa AsyncSession).

⚠️  IMPORTANTE: Este repositório é SÍNCRONO e deve ser usado com SessionLocal (sync),
não com AsyncSessionLocal. Para FastAPI, use FrequenciaRepository (async).
"""
from datetime import date
from uuid import UUID

from sqlalchemy import select, func, case
from sqlalchemy.orm import Session

from app.models.frequencia import Frequencia
from app.models.aluno import Aluno
from app.models.usuario import Usuario
from app.models.turma_professores import TurmaProfessores
from app.models.disciplina import Disciplina
from app.models.aluno_responsavel import AlunoResponsavel


class FrequenciaRepositorySync:
    """Repositório síncrono para operações de frequência em Celery."""

    def __init__(self, db: Session):
        """
        Args:
            db: Sessão SÍNCRONA do SQLAlchemy (SessionLocal, não AsyncSessionLocal)
        """
        self.db = db

    # ── Escrita ──────────────────────────────────────────────────────────────

    def registrar(self, frequencia: Frequencia) -> Frequencia:
        """Registra uma frequência (síncrono)."""
        self.db.add(frequencia)
        self.db.commit()
        self.db.refresh(frequencia)
        return frequencia

    # ── Leitura básica ────────────────────────────────────────────────────────

    def buscar_por_aluno_turma_data(
        self,
        aluno_id: UUID,
        turma_professor_id: UUID,
        data: date,
    ) -> Frequencia | None:
        """Busca frequência de um aluno em uma turma/professor em uma data (síncrono)."""
        return self.db.query(Frequencia).filter(
            Frequencia.fk_aluno == aluno_id,
            Frequencia.fk_turma_professor == turma_professor_id,
            Frequencia.data == data,
        ).first()

    # ── Índice de frequência de um aluno ─────────────────────────────────────

    def calcular_frequencia_aluno(
        self,
        aluno_id: UUID,
        turma_professor_id: UUID,
        data_inicio: date | None = None,
        data_fim: date | None = None,
    ) -> dict:
        """Calcula o percentual de frequência de um aluno (síncrono)."""
        query = self.db.query(
            func.count(Frequencia.id).label("total"),
            func.sum(
                case((Frequencia.presenca == True, 1), else_=0)
            ).label("presencas"),
        ).filter(
            Frequencia.fk_aluno == aluno_id,
            Frequencia.fk_turma_professor == turma_professor_id,
        )

        if data_inicio:
            query = query.filter(Frequencia.data >= data_inicio)
        if data_fim:
            query = query.filter(Frequencia.data <= data_fim)

        row = query.one()

        total = row.total or 0
        presencas = row.presencas or 0
        percentual = (presencas / total * 100) if total > 0 else 0.0

        return {
            "total_aulas": total,
            "total_presencas": presencas,
            "percentual": round(percentual, 2),
        }

    # ── Responsáveis do aluno ────────────────────────────────────────────────

    def buscar_responsaveis(self, aluno_id: UUID) -> list[dict]:
        """Busca todos os responsáveis de um aluno (síncrono)."""
        responsaveis = self.db.query(
            Usuario.id,
            Usuario.nome_completo,
            Usuario.email
        ).join(
            AlunoResponsavel,
            AlunoResponsavel.fk_responsavel == Usuario.id
        ).filter(
            AlunoResponsavel.fk_aluno == aluno_id
        ).all()

        return [
            {"id": r.id, "nome": r.nome_completo, "email": r.email}
            for r in responsaveis
        ]

    # ── Analytics: absenteísmo por turma ─────────────────────────────────────

    def absenteismo_por_turma(
        self,
        data_inicio: date | None = None,
        data_fim: date | None = None,
    ) -> list[dict]:
        """Calcula taxa de absenteísmo por turma/disciplina (síncrono)."""
        faltas_case = case((Frequencia.presenca == False, 1), else_=0)

        query = self.db.query(
            TurmaProfessores.fk_turma.label("turma_id"),
            Disciplina.nome.label("disciplina"),
            func.count(Frequencia.id).label("total_aulas"),
            func.sum(faltas_case).label("total_faltas"),
            (
                func.sum(faltas_case) * 100.0
                / func.nullif(func.count(Frequencia.id), 0)
            ).label("taxa_absenteismo"),
        ).join(
            TurmaProfessores,
            TurmaProfessores.id == Frequencia.fk_turma_professor
        ).join(
            Disciplina,
            Disciplina.id == TurmaProfessores.fk_disciplina
        ).group_by(
            TurmaProfessores.fk_turma,
            Disciplina.nome
        ).order_by(
            func.sum(faltas_case).desc()
        )

        if data_inicio:
            query = query.filter(Frequencia.data >= data_inicio)
        if data_fim:
            query = query.filter(Frequencia.data <= data_fim)

        rows = query.all()

        return [
            {
                "turma_id": str(r.turma_id),
                "disciplina": r.disciplina,
                "total_aulas": r.total_aulas,
                "total_faltas": r.total_faltas,
                "taxa_absenteismo": round(float(r.taxa_absenteismo or 0), 2),
            }
            for r in rows
        ]

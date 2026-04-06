"""
Repositório síncrono para Nota.
Usado exclusivamente por tasks Celery (não usa AsyncSession).

⚠️  IMPORTANTE: Este repositório é SÍNCRONO e deve ser usado com SessionLocal (sync),
não com AsyncSessionLocal. Para FastAPI, use NotaRepository (async).
"""
from decimal import Decimal
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.nota import Nota
from app.models.avaliacao import Avaliacao
from app.models.turma_professores import TurmaProfessores
from app.models.disciplina import Disciplina
from app.models.professor import Professor
from app.models.funcionario import Funcionario
from app.models.turma import Turma


class NotaRepositorySync:
    """Repositório síncrono para operações de nota em Celery."""

    def __init__(self, db: Session):
        """
        Args:
            db: Sessão SÍNCRONA do SQLAlchemy (SessionLocal, não AsyncSessionLocal)
        """
        self.db = db

    # ── Avaliações ────────────────────────────────────────────────────────────

    def criar_avaliacao(self, avaliacao: Avaliacao) -> Avaliacao:
        """Cria uma avaliação (síncrono)."""
        self.db.add(avaliacao)
        self.db.commit()
        self.db.refresh(avaliacao)
        return avaliacao

    def buscar_avaliacao(self, avaliacao_id: UUID) -> Avaliacao | None:
        """Busca uma avaliação por ID (síncrono)."""
        return self.db.query(Avaliacao).filter(
            Avaliacao.id == avaliacao_id
        ).first()

    # ── Notas ─────────────────────────────────────────────────────────────────

    def criar_nota(self, nota: Nota) -> Nota:
        """Cria uma nota (síncrono)."""
        self.db.add(nota)
        self.db.commit()
        self.db.refresh(nota)
        return nota

    def buscar_nota(self, nota_id: UUID) -> Nota | None:
        """Busca uma nota por ID (síncrono)."""
        return self.db.query(Nota).filter(
            Nota.id == nota_id
        ).first()

    def buscar_nota_por_aluno_avaliacao(
        self,
        aluno_id: UUID,
        avaliacao_id: UUID
    ) -> Nota | None:
        """Busca uma nota específica do aluno em uma avaliação (síncrono)."""
        return self.db.query(Nota).filter(
            Nota.fk_aluno == aluno_id,
            Nota.fk_avaliacao == avaliacao_id,
        ).first()

    def atualizar_nota(self, nota: Nota, novo_valor: Decimal) -> Nota:
        """Atualiza o valor de uma nota (síncrono)."""
        nota.valor = novo_valor
        self.db.commit()
        self.db.refresh(nota)
        return nota

    # ── Ownership: professor → turma ──────────────────────────────────────────

    def professor_owns_turma(
        self,
        user_id: str,
        turma_professor_id: UUID
    ) -> bool:
        """Verifica se o usuário é professor daquela turma/disciplina (síncrono)."""
        resultado = self.db.query(TurmaProfessores).join(
            Professor,
            Professor.id == TurmaProfessores.fk_professor
        ).join(
            Funcionario,
            Funcionario.id == Professor.fk_funcionario
        ).filter(
            TurmaProfessores.id == turma_professor_id,
            Funcionario.fk_usuario == UUID(user_id),
        ).first()
        return resultado is not None

    # ── Notas do aluno para o boletim ─────────────────────────────────────────

    def notas_do_aluno(
        self,
        aluno_id: UUID,
        ano_letivo: str,
    ) -> list[dict]:
        """Retorna todas as notas do aluno com contexto de disciplina e período (síncrono)."""
        notas = self.db.query(
            Nota.id.label("nota_id"),
            Nota.valor,
            Avaliacao.peso,
            Avaliacao.periodo,
            Avaliacao.titulo,
            Avaliacao.tipo,
            Disciplina.id.label("disciplina_id"),
            Disciplina.nome.label("disciplina_nome"),
            TurmaProfessores.fk_turma.label("turma_id"),
        ).join(
            Avaliacao,
            Avaliacao.id == Nota.fk_avaliacao
        ).join(
            TurmaProfessores,
            TurmaProfessores.id == Avaliacao.fk_turma_professor
        ).join(
            Disciplina,
            Disciplina.id == TurmaProfessores.fk_disciplina
        ).join(
            Turma,
            Turma.id == TurmaProfessores.fk_turma
        ).filter(
            Nota.fk_aluno == aluno_id,
            Turma.ano_letivo == str(ano_letivo),
        ).order_by(
            Disciplina.nome,
            Avaliacao.periodo
        ).all()

        return [
            {
                "nota_id": r.nota_id,
                "valor": float(r.valor) if r.valor is not None else None,
                "peso": float(r.peso),
                "periodo": r.periodo,
                "titulo": r.titulo,
                "tipo": r.tipo,
                "disciplina_id": r.disciplina_id,
                "disciplina_nome": r.disciplina_nome,
                "turma_id": r.turma_id,
            }
            for r in notas
        ]

    # ── Média da turma por disciplina/período ─────────────────────────────────

    def media_turma(
        self,
        turma_professor_id: UUID,
        periodo: str,
    ) -> float:
        """Calcula a média ponderada de todos os alunos da turma (síncrono)."""
        resultado = self.db.query(
            func.sum(Nota.valor * Avaliacao.peso).label("soma_ponderada"),
            func.sum(Avaliacao.peso).label("soma_pesos"),
        ).join(
            Avaliacao,
            Avaliacao.id == Nota.fk_avaliacao
        ).filter(
            Avaliacao.fk_turma_professor == turma_professor_id,
            Avaliacao.periodo == periodo,
        ).first()

        if not resultado or not resultado.soma_pesos:
            return 0.0

        return round(float(resultado.soma_ponderada / resultado.soma_pesos), 2)

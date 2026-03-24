import logging
import os
import uuid
from datetime import date
from uuid import UUID

from app.core import config
from app.models.frequencia import Frequencia
from app.repositories.aluno_repository import AlunoRepository
from app.repositories.disciplina_repository import DisciplinaRepository
from app.repositories.frequencia_repository import FrequenciaRepository
from app.repositories.turma_professores_repository import TurmaProfessoresRepository
from app.repositories.turma_repository import TurmaRepository
from app.tasks.attendance_tasks import alertar_frequencia_critica
from app.schemas.frequencia import FrequenciaCreate

logger = logging.getLogger("attendance")

FREQUENCIA_MINIMA = config.Settings().FREQUENCIA_MINIMA


class FrequenciaService:
    def __init__(self, repo: FrequenciaRepository, alunoRepo: AlunoRepository, disciplinaRepo: DisciplinaRepository, turmaProfessorRepo: TurmaProfessoresRepository, turmaRepo: TurmaRepository):
        self.repo = repo
        self.alunoRepo = alunoRepo
        self.disciplinaRepo = disciplinaRepo
        self.turmaProfessorRepo = turmaProfessorRepo
        self.turmaRepo = turmaRepo

    # ── Registro de presença ──────────────────────────────────────────────────

    async def registrar(
        self,
        body: FrequenciaCreate,
        registrado_por: str
    ) -> Frequencia:

        existente = await self.repo.buscar_por_aluno_turma_data(
            aluno_id=body.aluno_id,
            turma_professor_id=body.turma_professor_id,
            data=body.data,
        )

        if existente:
            # Correção de lançamento
            existente.presenca = body.presenca
            existente.metodo_registro = "MANUAL_CORRECAO"

            await self.repo.db.commit()
            await self.repo.db.refresh(existente)

            frequencia = existente
        else:
            frequencia = Frequencia(
                id=uuid.uuid4(),
                fk_aluno=body.aluno_id,
                fk_turma_professor=body.turma_professor_id,
                data=body.data,
                presenca=body.presenca,
                metodo_registro="MANUAL",
            )

            frequencia = await self.repo.registrar(frequencia)

        # Verifica alerta em background
        await self._verificar_alerta_frequencia(
            aluno_id=body.aluno_id,
            turma_professor_id=body.turma_professor_id,
        )

        return frequencia

    # ── Alerta de frequência crítica ─────────────────────────────────────────

    async def _verificar_alerta_frequencia(
        self,
        aluno_id: UUID,
        turma_professor_id: UUID,
    ) -> None:

        stats = await self.repo.calcular_frequencia_aluno(
            aluno_id=aluno_id,
            turma_professor_id=turma_professor_id,
        )
        
        turma_professor = await self.turmaProfessorRepo.get_vinculo_by_id(turma_professor_id)
        disciplina = await self.disciplinaRepo.get_disciplina_by_id(turma_professor.fk_disciplina)
        turma = await self.turmaRepo.get_turma_by_id(turma_professor.fk_turma)

        if stats["total_aulas"] < 5:
            return

        if stats["percentual"] < FREQUENCIA_MINIMA:
            responsaveis = await self.repo.buscar_responsaveis(aluno_id)
            aluno = await self.alunoRepo.get_aluno_by_id(aluno_id)

            alertar_frequencia_critica.delay(
                aluno_id=str(aluno_id),
                aluno_nome=aluno.usuario.nome_completo,
                disciplina_nome=disciplina.nome,
                turma_id=str(turma.id),
                frequencia_atual=stats["percentual"],
                responsaveis=responsaveis,
            )

            logger.warning(
                "frequencia_critica",
                extra={
                    "aluno": aluno.usuario.nome_completo,
                    "disciplina": disciplina.nome,
                    "frequencia": stats["percentual"],
                    "turma": turma.id,
                    "responsaveis": responsaveis,
                },
            )

    # ── Analytics ─────────────────────────────────────────────────────────────

    async def analytics(
        self,
        data_inicio: date | None = None,
        data_fim: date | None = None,
    ) -> dict:

        absenteismo = await self.repo.absenteismo_por_turma(data_inicio, data_fim)
        top_faltas = await self.repo.top_faltas(data_inicio, data_fim)

        return {
            "absenteismo_por_turma": absenteismo,
            "top_10_alunos_mais_faltas": top_faltas,
        }

    # ── Dados para PDF ────────────────────────────────────────────────────────

    async def dados_relatorio(
        self,
        data_inicio: date,
        data_fim: date
    ) -> dict:

        tendencia = await self.repo.tendencia_frequencia_por_turma(
            data_inicio,
            data_fim
        )

        top_faltas = await self.repo.top_faltas(
            data_inicio,
            data_fim,
            limit=10
        )

        return {
            "periodo": {
                "inicio": str(data_inicio),
                "fim": str(data_fim),
            },
            "tendencia": tendencia,
            "top_faltas": top_faltas,
        }
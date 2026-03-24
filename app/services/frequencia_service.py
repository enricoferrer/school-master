import logging
import uuid
from datetime import date
from uuid import UUID

from app.models.frequencia import Frequencia
from app.repositories.frequencia_repository import FrequenciaRepository
from app.tasks.attendance_tasks import alertar_frequencia_critica
from app.schemas.frequencia import FrequenciaCreate

logger = logging.getLogger("attendance")

FREQUENCIA_MINIMA = 75.0


class FrequenciaService:
    def __init__(self, repo: FrequenciaRepository):
        self.repo = repo

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

        if stats["total_aulas"] < 5:
            return

        if stats["percentual"] < FREQUENCIA_MINIMA:
            responsaveis = await self.repo.buscar_responsaveis(aluno_id)

            alertar_frequencia_critica.delay(
                aluno_id=str(aluno_id),
                aluno_nome="N/D",
                disciplina_nome="N/D",
                turma_id=str(turma_professor_id),
                frequencia_atual=stats["percentual"],
                responsaveis=responsaveis,
            )

            logger.warning(
                "Frequência crítica enfileirada para alerta",
                extra={
                    "aluno_id": str(aluno_id),
                    "frequencia": stats["percentual"],
                    "total_aulas": stats["total_aulas"],
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
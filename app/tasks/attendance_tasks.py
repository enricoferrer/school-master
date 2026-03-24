"""
Tarefas Celery para alertas de frequência.

Rodar o worker com:
    celery -A app.core.celery worker --loglevel=info
"""
import logging
import asyncio
from typing import List, Dict

from app.core.celery import celery_app

logger = logging.getLogger("attendance.alerts")


async def processar_alerta_frequencia(
    aluno_id: str,
    aluno_nome: str,
    disciplina_nome: str,
    turma_id: str,
    frequencia_atual: float,
    responsaveis: List[Dict],
):
    nomes_responsaveis = ", ".join(
        [r.get("nome", "N/D") for r in responsaveis]
    ) or "N/D"

    logger.warning(
        f"🚨 ALERTA DE FREQUÊNCIA\n"
        f"Aluno: {aluno_nome}\n"
        f"Disciplina: {disciplina_nome}\n"
        f"Frequência: {frequencia_atual:.1f}% (mínimo: 75%)\n"
        f"Turma: {turma_id}\n"
        f"Responsáveis: {nomes_responsaveis}"
    )

    logger.warning(
        "frequencia_critica",
        extra={
            "alert_type": "frequencia_abaixo_minimo",
            "aluno_id": aluno_id,
            "aluno_nome": aluno_nome,
            "disciplina": disciplina_nome,
            "turma_id": turma_id,
            "frequencia_atual": frequencia_atual,
            "minimo_legal": 75,
            "responsaveis": responsaveis,
        },
    )

@celery_app.task(
    name="tasks.alertar_frequencia_critica",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    autoretry_for=(Exception,),
    retry_backoff=True,          
    retry_jitter=True,           
)
def alertar_frequencia_critica(
    self,
    aluno_id: str,
    aluno_nome: str,
    disciplina_nome: str,
    turma_id: str,
    frequencia_atual: float,
    responsaveis: List[Dict],
) -> None:
    """
    Task síncrona que executa lógica async com segurança.
    """
    try:
        logger.info(
            f"[TASK START] Alerta frequência | aluno={aluno_nome} ({aluno_id})"
        )

        asyncio.run(
            processar_alerta_frequencia(
                aluno_id=aluno_id,
                aluno_nome=aluno_nome,
                disciplina_nome=disciplina_nome,
                turma_id=turma_id,
                frequencia_atual=frequencia_atual,
                responsaveis=responsaveis,
            )
        )

        logger.info(
            f"[TASK SUCCESS] Alerta enviado | aluno={aluno_nome} ({aluno_id})"
        )

    except Exception as exc:
        logger.error(
            f"[TASK ERROR] Falha no alerta | aluno={aluno_nome} ({aluno_id})",
            exc_info=True,
        )
        raise exc 
import logging
from app.core.celery import celery_app

logger = logging.getLogger("grades.alerts")


@celery_app.task(
    name                = "tasks.alertar_nota_editada",
    bind                = True,
    max_retries         = 3,
    default_retry_delay = 60,
    queue               = "grades",    # ← fila separada das de frequência
)
def alertar_nota_editada(
    self,
    nota_id:          str,
    aluno_id:         str,
    aluno_nome:       str,
    disciplina_nome:  str,
    avaliacao_titulo: str,
    professor_id:     str,
    valor_anterior:   float | None,
    valor_novo:       float,
    periodo:          str,
) -> None:
    """
    Alerta quando uma nota lançada é editada.
    Fila: grades (RabbitMQ)
    ⚠️  IMPORTANTE: Task SÍNCRONA - sem operações async
    """
    try:
        variacao = round(valor_novo - (valor_anterior or 0), 2)
        direcao  = "⬆️ subiu" if variacao > 0 else "⬇️ baixou"

        logger.warning(
            "📝 NOTA EDITADA — ALERTA",
            extra={
                "alert_type":      "NOTA_EDITADA",
                "nota_id":         nota_id,
                "aluno_id":        aluno_id,
                "aluno_nome":      aluno_nome,
                "disciplina":      disciplina_nome,
                "avaliacao":       avaliacao_titulo,
                "periodo":         periodo,
                "professor_id":    professor_id,
                "valor_anterior":  valor_anterior,
                "valor_novo":      valor_novo,
                "variacao":        f"{'+' if variacao >= 0 else ''}{variacao} ({direcao})",
            },
        )
        logger.info(f"✅ Alerta de nota registrado: {aluno_nome} - {disciplina_nome}")
        # TODO: inserir em notificacoes + e-mail ao coordenador

    except Exception as exc:
        logger.error("❌ Falha na task alertar_nota_editada: %s", exc, exc_info=True)
        raise self.retry(exc=exc)
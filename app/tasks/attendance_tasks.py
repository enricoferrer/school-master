from app.tasks.notificacao_tasks import disparar_notificacao, processar_notificacao
import logging
from app.core.celery   import celery_app

logger = logging.getLogger("attendance.alerts")

@celery_app.task(
    name="tasks.alertar_frequencia_critica",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    queue="attendance",
)
def alertar_frequencia_critica(
    self,
    aluno_id: str,
    aluno_nome: str,
    disciplina_nome: str,
    turma_id: str,
    frequencia_atual: float,
    responsaveis: list[dict],
) -> None:
    """
    Alerta sobre frequência crítica de um aluno.
    ⚠️  IMPORTANTE: Task SÍNCRONA que dispara outras tasks async
    """

    try:
        logger.warning(
            "🚨 ALERTA DE FREQUÊNCIA CRÍTICA",
            extra={
                "task_id": self.request.id,
                "aluno_id": aluno_id,
                "frequencia": frequencia_atual,
                "responsaveis_count": len(responsaveis),
            },
        )

        for resp in responsaveis:
            usuario_id = resp.get("id") or resp.get("usuario_id")
            email = resp.get("email")

            if usuario_id is None or email is None:
                logger.error(f"Responsável inválido (id={usuario_id}, email={email}), pulando...")
                continue

            try:
                disparar_notificacao.delay(
                    usuario_id=str(usuario_id),
                    email_destino=email,
                    tipo_evento="FREQUENCIA_CRITICA",
                    titulo="Alerta de Frequência Crítica",
                    mensagem=(
                        f"O aluno {aluno_nome} está com frequência crítica "
                        f"na disciplina {disciplina_nome} ({frequencia_atual:.1f}%)."
                    ),
                )
                logger.info(f"✅ Notificação enfileirada para {email}")
            except Exception as inner_exc:
                logger.error(f"Erro ao enfileirar notificação: {inner_exc}", exc_info=True)
                # Não falha a task inteira, continua com próximos responsáveis

    except Exception as exc:
        logger.error(
            "❌ Erro na alertar_frequencia_critica",
            exc_info=True,
        )
        raise self.retry(exc=exc)


@celery_app.task(
    name="tasks.alertar_falta",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    queue="attendance",
)
def alertar_falta(
    self,
    aluno_id: str,
    aluno_nome: str,
    disciplina_nome: str,
    data_falta: str,
    responsaveis: list[dict],
) -> None:
    """
    Alerta sobre registro de falta de um aluno.
    ⚠️  IMPORTANTE: Task SÍNCRONA que dispara outras tasks async
    """

    try:
        logger.info(
            "⚠️ ALERTA DE FALTA REGISTRADA",
            extra={
                "task_id": self.request.id,
                "aluno_id": aluno_id,
                "data": data_falta,
                "responsaveis_count": len(responsaveis),
            },
        )

        for resp in responsaveis:
            usuario_id = resp.get("id") or resp.get("usuario_id")
            email = resp.get("email")

            if usuario_id is None or email is None:
                logger.error(f"Responsável inválido (id={usuario_id}, email={email}), pulando...")
                continue

            try:
                disparar_notificacao.delay(
                    usuario_id=str(usuario_id),
                    email_destino=email,
                    tipo_evento="FALTA",
                    titulo="Registro de Falta",
                    mensagem=(
                        f"Uma falta foi registrada para o aluno {aluno_nome} "
                        f"em {data_falta} na disciplina {disciplina_nome}."
                    ),
                )
                logger.info(f"✅ Notificação de falta enfileirada para {email}")
            except Exception as inner_exc:
                logger.error(f"Erro ao enfileirar notificação de falta: {inner_exc}", exc_info=True)
                # Não falha a task inteira, continua com próximos responsáveis

    except Exception as exc:
        logger.error(
            "❌ Erro na alertar_falta",
            exc_info=True,
        )
        raise self.retry(exc=exc)
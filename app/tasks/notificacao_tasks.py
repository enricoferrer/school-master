import logging
import smtplib
import uuid
from datetime import datetime, timezone, time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.celery import celery_app
from app.core.config import settings

logger = logging.getLogger("notificacoes")


# ── Task principal ──────────────────────────────────────────────────────────

@celery_app.task(
    name="tasks.processar_notificacao",
    bind=True,
    max_retries=3,
    default_retry_delay=120,
    queue="notificacoes",
)
def processar_notificacao(
    self,
    notificacao_id: str,
    usuario_id: str,
    email_destino: str,
    titulo: str,
    mensagem: str,
    tipo_evento: str,
    horario_inicio: str | None,
    horario_fim: str | None,
):
    """
    Processa e envia notificação de email de forma síncrona.
    ⚠️  IMPORTANTE: Usa sessão SÍNCRONA do SQLAlchemy (sem asyncio)
    """
    from app.core.database import SessionLocal
    from app.repositories.notificacao_repository_sync import NotificacaoRepositorySync

    db = None
    try:
        db = SessionLocal()
        repo = NotificacaoRepositorySync(db)

        # ⏰ janela de envio
        if not _dentro_da_janela(horario_inicio, horario_fim):
            logger.info(f"Notificação {notificacao_id} adiada (fora da janela)")
            processar_notificacao.apply_async(
                kwargs={
                    "notificacao_id": notificacao_id,
                    "usuario_id": usuario_id,
                    "email_destino": email_destino,
                    "titulo": titulo,
                    "mensagem": mensagem,
                    "tipo_evento": tipo_evento,
                    "horario_inicio": horario_inicio,
                    "horario_fim": horario_fim,
                },
                countdown=1800,
            )
            return

        _enviar_email(email_destino, titulo, mensagem)
        repo.atualizar_status(uuid.UUID(notificacao_id), "ENVIADO")
        db.commit()

        logger.info(f"✅ Notificação enviada: {email_destino}")

    except Exception as exc:
        if db:
            try:
                repo = NotificacaoRepositorySync(db)
                repo.atualizar_status(
                    uuid.UUID(notificacao_id),
                    "FALHOU",
                    erro_detalhe=str(exc),
                )
                db.commit()
            except Exception as inner_exc:
                logger.error(f"Erro ao atualizar status: {inner_exc}")
                if db:
                    db.rollback()

        logger.error(f"Erro ao enviar notificação {notificacao_id}: {exc}", exc_info=True)
        raise self.retry(exc=exc)
    
    finally:
        if db:
            db.close()


# ── Dispatcher ──────────────────────────────────────────────────────────────

@celery_app.task(
    name="tasks.disparar_notificacao",
    queue="notificacoes",
)
def disparar_notificacao(
    usuario_id: str,
    email_destino: str,
    tipo_evento: str,
    titulo: str,
    mensagem: str,
    horario_inicio: str | None = None,
    horario_fim: str | None = None,
):
    """
    Dispara (enfileira) uma notificação para processamento.
    ⚠️  IMPORTANTE: Usa sessão SÍNCRONA do SQLAlchemy (sem asyncio)
    """
    from app.core.database import SessionLocal
    from app.models.notificacao import Notificacao
    from app.repositories.notificacao_repository_sync import NotificacaoRepositorySync

    db = None
    try:
        db = SessionLocal()
        repo = NotificacaoRepositorySync(db)

        notif = Notificacao(
            id=uuid.uuid4(),
            fk_usuario_destino=uuid.UUID(usuario_id),
            tipo=tipo_evento,
            canal="EMAIL",
            titulo=titulo,
            mensagem=mensagem,
            status="PENDENTE",
        )

        # ⚠️ Adiciona manualmente em vez de usar criar() que pode estar async
        db.add(notif)
        db.commit()
        db.refresh(notif)

        logger.info(f"📨 Notificação enfileirada para {email_destino}")

        processar_notificacao.delay(
            notificacao_id=str(notif.id),
            usuario_id=usuario_id,
            email_destino=email_destino,
            titulo=titulo,
            mensagem=mensagem,
            tipo_evento=tipo_evento,
            horario_inicio=horario_inicio,
            horario_fim=horario_fim,
        )

    except Exception as exc:
        logger.error(f"Erro ao disparar notificação: {exc}", exc_info=True)
        if db:
            db.rollback()
        raise

    finally:
        if db:
            db.close()


# ── Helpers ─────────────────────────────────────────────────────────────────

def _dentro_da_janela(inicio_str, fim_str):
    if not inicio_str or not fim_str:
        return True

    agora = datetime.now(timezone.utc).time().replace(tzinfo=None)
    inicio = time.fromisoformat(inicio_str)
    fim = time.fromisoformat(fim_str)

    if inicio <= fim:
        return inicio <= agora <= fim

    return agora >= inicio or agora <= fim


def _enviar_email(destino, titulo, mensagem):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = titulo
    msg["From"] = settings.SMTP_FROM
    msg["To"] = destino

    html = f"""
    <html><body>
      <h3>{titulo}</h3>
      <p>{mensagem}</p>
    </body></html>
    """

    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.sendmail(settings.SMTP_FROM, destino, msg.as_string())
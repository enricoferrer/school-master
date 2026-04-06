"""
Repositório síncrono para Notificações.
Usado exclusivamente por tasks Celery (não usa AsyncSession).

⚠️  IMPORTANTE: Este repositório é SÍNCRONO e deve ser usado com SessionLocal (sync),
não com AsyncSessionLocal. Para FastAPI, use NotificacaoRepository (async).
"""
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import update, select
from sqlalchemy.orm import Session

from app.models.notificacao import Notificacao


class NotificacaoRepositorySync:
    """Repositório síncrono para operações de notificação em Celery."""

    def __init__(self, db: Session):
        """
        Args:
            db: Sessão SÍNCRONA do SQLAlchemy (SessionLocal, não AsyncSessionLocal)
        """
        self.db = db

    def criar(self, notificacao: Notificacao) -> Notificacao:
        """Cria uma notificação (síncrono)."""
        self.db.add(notificacao)
        self.db.commit()
        self.db.refresh(notificacao)
        return notificacao

    def atualizar_status(
        self,
        notificacao_id: UUID,
        status: str,
        erro_detalhe: str | None = None,
    ) -> None:
        """Atualiza o status de uma notificação (síncrono)."""
        valores = {
            "status": status,
            "tentativas": Notificacao.tentativas + 1,
        }

        if status == "ENVIADO":
            valores["enviado_em"] = datetime.now(timezone.utc)
            valores["erro_detalhe"] = None

        if erro_detalhe:
            valores["erro_detalhe"] = erro_detalhe

        self.db.execute(
            update(Notificacao)
            .where(Notificacao.id == notificacao_id)
            .values(**valores)
        )
        self.db.commit()

    def buscar(self, notificacao_id: UUID) -> Notificacao | None:
        """Busca uma notificação por ID (síncrono)."""
        return self.db.query(Notificacao).filter(
            Notificacao.id == notificacao_id
        ).first()

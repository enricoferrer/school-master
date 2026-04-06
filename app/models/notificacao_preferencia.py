import uuid
from sqlalchemy import Column, String, DateTime, Boolean, Time, ForeignKey, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base

class NotificacaoPreferencia(Base):
    __tablename__ = "notificacao_preferencias"

    id             = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    fk_usuario     = Column(UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    canal          = Column(String(20),  nullable=False, default="EMAIL")
    tipo_evento    = Column(String(50),  nullable=False)
    ativo          = Column(Boolean,     default=True)
    horario_inicio = Column(Time,        nullable=True)
    horario_fim    = Column(Time,        nullable=True)
    criado_em      = Column(DateTime(timezone=True), server_default=func.now())
    
    usuario = relationship("Usuario", back_populates="notificacao_preferencias")

    __table_args__ = (
        UniqueConstraint("fk_usuario", "canal", "tipo_evento",
                         name="uq_preferencia_usuario_canal_evento"),
    )
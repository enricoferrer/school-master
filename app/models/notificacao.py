import uuid
from sqlalchemy import Column, String, Text, Integer, DateTime, Boolean, Time, ForeignKey, func, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base


class Notificacao(Base):
    __tablename__ = "notificacoes"

    id                 = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    fk_usuario_destino = Column(UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    tipo               = Column(String(50),  nullable=True)
    canal              = Column(String(20),  nullable=True)
    titulo             = Column(String,      nullable=True)
    mensagem           = Column(Text,        nullable=True)
    status             = Column(String(20),  default="PENDENTE")
    tentativas         = Column(Integer,     default=0)
    enviado_em         = Column(DateTime(timezone=True), nullable=True)
    erro_detalhe       = Column(Text,        nullable=True)
    criado_em          = Column(DateTime(timezone=True), server_default=func.now())

    usuario_destino = relationship("Usuario", back_populates="notificacoes_recebidas")

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.core.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    fk_usuario = Column(UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True)
    operacao = Column(String, nullable=False)
    tabela_afetada = Column(String, nullable=False)
    registro_id = Column(UUID(as_uuid=True), nullable=True)
    dados_anteriores = Column(JSONB, nullable=True)
    dados_posteriores = Column(JSONB, nullable=True)
    ip_origem = Column(String, nullable=True)
    user_agent = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), default=func.now())
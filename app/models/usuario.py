import datetime
from uuid import uuid4
from sqlalchemy import TIMESTAMP, Boolean, Column, DateTime, ForeignKey, Integer, String, UUID, Date, func
from app.core.database import Base
from sqlalchemy.orm import relationship

class Usuario(Base):
    __tablename__ = 'usuarios'
    
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    nome_completo = Column(String, nullable=False)
    nome_social = Column(String)
    data_nascimento = Column(Date, nullable=False)
    cpf = Column(String, nullable=False, unique=True)
    registro_geral = Column(String, nullable=False, unique=True)
    genero = Column(String, nullable=False)
    email = Column(String, nullable=False)
    telefone = Column(String)
    endereco = Column(String, nullable=False)
    fk_role = Column(UUID(as_uuid=True), ForeignKey("roles.id", ondelete="NO ACTION", onupdate="NO ACTION"), nullable=False)
    senha_hash = Column(String, nullable=True)
    tentativas_falhas = Column(Integer, default=0)
    bloqueado_ate = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)
    criado_em = Column(DateTime(timezone=True), default=func.now())
    atualizado_em = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    funcionario = relationship("Funcionario", back_populates="usuario", cascade="all, delete")
    aluno = relationship("Aluno", back_populates="usuario", cascade="all, delete-orphan")
    role = relationship("Role", back_populates="usuarios", foreign_keys=[fk_role])
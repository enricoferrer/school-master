from uuid import uuid4
from sqlalchemy import Column, String, UUID, Date
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
    
    funcionario = relationship("Funcionario", back_populates="usuario", cascade="all, delete")
    aluno = relationship("Aluno", back_populates="usuario", cascade="all, delete-orphan")
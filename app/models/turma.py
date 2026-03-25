from uuid import uuid4

from sqlalchemy import Column, String, UUID
from sqlalchemy.orm import relationship
from app.core.database import Base

class Turma(Base):
    __tablename__ = "turmas"
    
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    sala = Column(String)
    serie = Column(String)
    ano_letivo = Column(String)
    
    turma_professores = relationship("TurmaProfessores", back_populates="turma", cascade="all, delete-orphan")
    aluno = relationship("Aluno", back_populates="turma", cascade="all, delete-orphan")
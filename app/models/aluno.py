from uuid import uuid4

from sqlalchemy import UUID, Column, Date, ForeignKey, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class Aluno(Base):
    __tablename__ = "alunos"
    
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    matricula = Column(String, nullable=False, unique=True)
    data_matricula = Column(Date, nullable=False)
    fk_turma = Column(UUID(as_uuid=True), ForeignKey("turmas.id", ondelete="NO ACTION", onupdate="NO ACTION"), nullable=True)
    fk_usuario = Column(UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="NO ACTION", onupdate="NO ACTION"), nullable=False)
    
    turma = relationship("Turma", back_populates="aluno", foreign_keys=[fk_turma])
    usuario = relationship("Usuario", back_populates="aluno", foreign_keys=[fk_usuario])
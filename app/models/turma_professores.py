from uuid import uuid4

from sqlalchemy import UUID, Column, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class TurmaProfessores(Base):
    __tablename__ = "turma_professores"
    
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    fk_turma = Column(UUID(as_uuid=True), ForeignKey("turmas.id", ondelete="NO ACTION", onupdate="NO ACTION"), nullable=False)
    fk_professor = Column(UUID(as_uuid=True), ForeignKey("professores.id", ondelete="NO ACTION", onupdate="NO ACTION"), nullable=False)
    fk_disciplina = Column(UUID(as_uuid=True), ForeignKey("disciplinas.id", ondelete="NO ACTION", onupdate="NO ACTION"), nullable=False)
    
    turma = relationship("Turma", back_populates="turma_professores", foreign_keys=[fk_turma])
    professor = relationship("Professor", back_populates="turma_professores", foreign_keys=[fk_professor])
    disciplina = relationship("Disciplina", back_populates="turma_professores", foreign_keys=[fk_disciplina])
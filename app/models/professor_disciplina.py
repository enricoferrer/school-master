from app.core.database import Base
from sqlalchemy import Column, UUID, ForeignKey
from uuid import uuid4
from sqlalchemy.orm import relationship

class ProfessorDisciplina(Base):
    __tablename__ = "professor_disciplinas"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    fk_professor = Column(UUID(as_uuid=True), ForeignKey("professores.id", ondelete="NO ACTION", onupdate="NO ACTION"), nullable=False)
    fk_disciplina = Column(UUID(as_uuid=True), ForeignKey("disciplinas.id", ondelete="NO ACTION", onupdate="NO ACTION"), nullable=False)

    professor = relationship("Professor", back_populates="professor_disciplinas", foreign_keys=[fk_professor])
    disciplina = relationship("Disciplina", back_populates="professor_disciplinas", foreign_keys=[fk_disciplina])
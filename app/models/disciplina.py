from app.core.database import Base
from sqlalchemy import Column, String, UUID
from uuid import uuid4
from sqlalchemy.orm import relationship


class Disciplina(Base):
    __tablename__ = "disciplinas"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    nome = Column(String, nullable=False)
    codigo = Column(String, nullable=False, unique=True)

    professor_disciplinas = relationship("ProfessorDisciplina", back_populates="disciplina", cascade="all, delete-orphan")
    turma_professores = relationship("TurmaProfessores", back_populates="disciplina", cascade="all, delete-orphan")
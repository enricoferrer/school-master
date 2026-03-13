from app.core.database import Base
from sqlalchemy import Column, Integer, UUID, ForeignKey
from uuid import uuid4
from sqlalchemy.orm import relationship

class Professor(Base):
    __tablename__ = "professores"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    carga_horaria = Column(Integer, nullable=False)
    fk_funcionario = Column(UUID(as_uuid=True), ForeignKey("funcionarios.id", ondelete="NO ACTION", onupdate="NO ACTION"), nullable=False)

    funcionario = relationship("Funcionario", back_populates="professor", foreign_keys=[fk_funcionario])
    professor_disciplinas = relationship("ProfessorDisciplina", back_populates="professor", cascade="all, delete-orphan")
import uuid
from sqlalchemy import Column, String, Date, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base


class Frequencia(Base):
    __tablename__ = "frequencias"

    id                = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    fk_aluno          = Column(UUID(as_uuid=True), ForeignKey("alunos.id", ondelete="CASCADE"), nullable=False)
    fk_turma_professor= Column(UUID(as_uuid=True), ForeignKey("turma_professores.id", ondelete="CASCADE"), nullable=False)
    data              = Column(Date, nullable=False)
    presenca          = Column(Boolean, default=True)
    metodo_registro   = Column(String, default="MANUAL")
    
    turma_professores = relationship("TurmaProfessores", back_populates="frequencia", foreign_keys=[fk_turma_professor])
    aluno = relationship("Aluno", back_populates="frequencia", foreign_keys=[fk_aluno])

    __table_args__ = (
        UniqueConstraint(
            "fk_aluno", "fk_turma_professor", "data",
            name="uq_frequencia_aluno_turma_data",
        ),
    )
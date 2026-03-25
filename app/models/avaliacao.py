import uuid
from decimal import Decimal
from sqlalchemy import Column, String, Date, Numeric, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base


class Avaliacao(Base):
    __tablename__ = "avaliacoes"

    id                 = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    fk_turma_professor = Column(UUID(as_uuid=True), ForeignKey("turma_professores.id", ondelete="CASCADE"), nullable=False)
    titulo             = Column(String,  nullable=False)
    tipo               = Column(String,  nullable=True)
    peso               = Column(Numeric(5, 2), default=Decimal("1.0"))
    periodo            = Column(String(2), nullable=False) 
    data_aplicacao     = Column(Date, nullable=True)
    
    notas = relationship("Nota", back_populates="avaliacao", cascade="all, delete-orphan", passive_deletes=True)
    turma_professores = relationship("TurmaProfessores", back_populates="avaliacoes", foreign_keys=[fk_turma_professor])

    __table_args__ = (
        CheckConstraint("periodo IN ('1B','2B','3B','4B')", name="ck_avaliacoes_periodo"),
    )
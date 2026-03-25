import uuid
from sqlalchemy import Column, Numeric, DateTime, ForeignKey, func, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base


class Nota(Base):
    __tablename__ = "notas"

    id               = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    fk_aluno         = Column(UUID(as_uuid=True), ForeignKey("alunos.id",     ondelete="CASCADE"), nullable=False)
    fk_avaliacao     = Column(UUID(as_uuid=True), ForeignKey("avaliacoes.id", ondelete="CASCADE"), nullable=False)
    valor            = Column(Numeric(5, 2), nullable=True)
    data_lancamento  = Column(DateTime(timezone=True), server_default=func.now())
    
    aluno = relationship("Aluno", back_populates="notas", foreign_keys=[fk_aluno])
    avaliacao = relationship("Avaliacao", back_populates="notas", foreign_keys=[fk_avaliacao])

    __table_args__ = (
        UniqueConstraint("fk_aluno", "fk_avaliacao", name="uq_nota_aluno_avaliacao"),
    )
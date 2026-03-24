from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class AlunoResponsavel(Base):
    __tablename__ = "aluno_responsaveis"

    fk_aluno = Column(
        UUID(as_uuid=True),
        ForeignKey("alunos.id", ondelete="CASCADE"),
        primary_key=True,
    )

    fk_responsavel = Column(
        UUID(as_uuid=True),
        ForeignKey("usuarios.id", ondelete="CASCADE"),  # ✅ ajustado aqui
        primary_key=True,
    )

    parentesco = Column(String, nullable=True)

    is_financeiro = Column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )

    # relationships
    aluno = relationship("Aluno", back_populates="responsaveis")
    responsavel = relationship("Usuario", back_populates="alunos_responsavel")
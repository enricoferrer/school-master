from uuid import uuid4
from sqlalchemy import Column, String, UUID, Date, ForeignKey
from app.core.database import Base
from sqlalchemy.orm import relationship

class Funcionario(Base):
    __tablename__ = "funcionarios"
    
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    fk_usuario = Column(UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="NO ACTION", onupdate="NO ACTION"), nullable=False)
    data_admissao = Column(Date, nullable=False)
    matricula = Column(String, nullable=False)
    cargo = Column(String, nullable=False)
    
    usuario = relationship("Usuario", back_populates="funcionario", foreign_keys=[fk_usuario])
    professor = relationship("Professor", back_populates="funcionario", cascade="all, delete")
from uuid import uuid4

from sqlalchemy import Column, String, UUID
from app.core.database import Base

class Turma(Base):
    __tablename__ = "turmas"
    
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    sala = Column(String)
    serie = Column(String)
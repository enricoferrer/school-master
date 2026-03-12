from app.core.database import Base
from sqlalchemy import Column, String, UUID
from uuid import uuid4

class Disciplina(Base):
    __tablename__ = "disciplinas"
    
    id = Column(UUID, primary_key=True, index=True, default=uuid4)
    nome = Column(String, nullable=False)
    codigo = Column(String, nullable=False, unique=True)
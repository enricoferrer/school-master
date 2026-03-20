from uuid import uuid4

from sqlalchemy import Column, String
from sqlalchemy import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class Role(Base):
    __tablename__ = "roles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    nome = Column(String, nullable=False, unique=True)
    
    usuarios = relationship("Usuario", back_populates="role")
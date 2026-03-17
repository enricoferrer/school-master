from uuid import UUID

from sqlalchemy.orm import Session

from app.models.turma import Turma
from app.schemas.turma import TurmaCreate


class TurmaRepository:
    def __init__(self, db: Session):
        self.db = db
        
    def create(self, data: TurmaCreate):
        turma = Turma(**data.model_dump())
        self.db.add(turma)
        self.db.commit()
        self.db.refresh(turma)
        return turma
    
    def list_turmas(self):
        return self.db.query(Turma).all()
    
    def get_turma_by_id(self, id: UUID):
        return self.db.query(Turma).filter(Turma.id == id).first()
    
    def turma_existe(self, sala: str, serie: str) -> bool:
        turma = self.db.query(Turma).filter((Turma.sala == sala) & (Turma.serie == serie)).first()
        return bool(turma)
    
    def delete_turma(self, turma: Turma):
        self.db.delete(turma)
        self.db.commit()
from uuid import UUID

from sqlalchemy.orm import Session
from app.schemas.disciplina import DisciplinaCreate
from app.models.disciplina import Disciplina

class DisciplinaRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, data: DisciplinaCreate):
        disciplina = Disciplina(**data.model_dump())
        self.db.add(disciplina)
        self.db.commit()
        self.db.refresh(disciplina)
        return disciplina
    
    def list_disciplina(self):
        return self.db.query(Disciplina).all()
    
    def get_disciplina_by_id(self, id: UUID):
        return self.db.query(Disciplina).filter(Disciplina.id == id).first()
    
    def delete_disciplina(self, disciplina: Disciplina):
        self.db.delete(disciplina)
        self.db.commit()
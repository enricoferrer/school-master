from sqlalchemy.orm import Session
from uuid import UUID
from app.schemas.professor import ProfessorCreate
from app.models.professor import Professor

class ProfessorRepository:
    def __init__(self, db: Session):
        self.db = db
        
    def create(self, data: ProfessorCreate):
        professor = Professor(**data.model_dump())
        self.db.add(professor)
        self.db.commit()
        self.db.refresh(professor)
        return professor
    
    def list_all_professor(self):
        return self.db.query(Professor).all()
    
    def get_professor_by_id(self, id: UUID):
        return self.db.query(Professor).filter(Professor.id == id).first()
    
    def delete_professor(self, professor: Professor):
        self.db.delete(professor)
        self.db.commit()
from ast import Delete
from uuid import UUID

from sqlalchemy.orm import Session
from app.schemas.professor_disciplina import ProfessorDisciplinaCreate
from app.models.professor_disciplina import ProfessorDisciplina

class ProfessorDisciplinaRepository:
    def __init__(self, db: Session):
        self.db = db
        
    def create(self, data: ProfessorDisciplinaCreate):
        professor_disciplina = ProfessorDisciplina(**data.model_dump())
        self.db.add(professor_disciplina)
        self.db.commit()
        self.db.refresh(professor_disciplina)
        return professor_disciplina
        
    def vinculo_existe(self, fk_disciplina: UUID, fk_professor: UUID) -> bool:
        vinculo = self.db.query(ProfessorDisciplina).filter((ProfessorDisciplina.fk_disciplina == fk_disciplina) & (ProfessorDisciplina.fk_professor == fk_professor)).first()
        if vinculo:
            return True
        return False
    
    def list_disciplinas_do_professor(self, fk_professor: UUID):
        return self.db.query(ProfessorDisciplina).filter(ProfessorDisciplina.fk_professor == fk_professor).all()
    
    def list_professores_da_disciplina(self, fk_disciplina: UUID):
        return self.db.query(ProfessorDisciplina).filter(ProfessorDisciplina.fk_disciplina == fk_disciplina).all()
    
    def get_vinculo(self, fk_disciplina: UUID, fk_professor: UUID):
        vinculo = self.db.query(ProfessorDisciplina).filter((ProfessorDisciplina.fk_disciplina == fk_disciplina) & (ProfessorDisciplina.fk_professor == fk_professor)).first()
        return vinculo
    
    def delete_vinculo(self, vinculo: ProfessorDisciplina):
        self.db.delete(vinculo)
        self.db.commit()
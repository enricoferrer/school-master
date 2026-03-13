from pydantic import BaseModel
from uuid import UUID
from app.schemas.professor import ProfessorResponse
from app.schemas.disciplina import DisciplinaResponse

class ProfessorDisciplinaBase(BaseModel):
    fk_professor: UUID
    fk_disciplina: UUID
    
class ProfessorDisciplinaCreate(ProfessorDisciplinaBase):
    pass

class ProfessorDisciplinaResponse(ProfessorDisciplinaBase):
    id: UUID
    professor: ProfessorResponse
    disciplina: DisciplinaResponse
    
    model_config = {'from_attributes': True}
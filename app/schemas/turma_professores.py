from uuid import UUID

from pydantic import BaseModel

from app.schemas.disciplina import DisciplinaResponse
from app.schemas.professor import ProfessorResponse
from app.schemas.turma import TurmaResponse


class TurmaProfessoresBase(BaseModel):
    fk_professor: UUID
    fk_turma: UUID
    fk_disciplina: UUID
    
class TurmaProfessoresCreate(TurmaProfessoresBase):
    pass

class TurmaProfessoresResponse(TurmaProfessoresBase):
    id: UUID
    professor: ProfessorResponse
    disciplina: DisciplinaResponse
    turma: TurmaResponse
    
    model_config = {'from_attributes': True}
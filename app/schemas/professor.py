from uuid import UUID

from pydantic import BaseModel


class ProfessorBase(BaseModel):
    fk_funcionario: UUID
    carga_horaria: int
    
class ProfessorCreate(ProfessorBase):
    pass

class ProfessorResponse(ProfessorBase):
    id: UUID
    
    model_config = {'from_attributes': True}
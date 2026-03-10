from uuid import UUID

from pydantic import BaseModel, field_validator
from app.validators.professor_validator import validate_carga_horaria

class ProfessorBase(BaseModel):
    fk_funcionario: UUID
    carga_horaria: int
    
    @field_validator("carga_horaria")
    @classmethod
    def val_carga_horaria(cls, v): return validate_carga_horaria(v)
    
class ProfessorCreate(ProfessorBase):
    pass

class ProfessorResponse(ProfessorBase):
    id: UUID
    
    model_config = {'from_attributes': True}
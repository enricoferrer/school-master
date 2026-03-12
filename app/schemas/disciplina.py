from uuid import UUID

from pydantic import BaseModel, field_validator
from app.validators.common_validator import (
    not_empty
)
from app.validators.disciplina_validator import (
    validate_nome,
    validate_codigo
)

class DisciplinaModel(BaseModel):
    nome: str
    codigo: str
    
    @field_validator("nome", "codigo")
    @classmethod
    def val_not_empty(cls, v): return not_empty(v)
    
    @field_validator("nome")
    @classmethod
    def val_nome(cls, v): return validate_nome(v)
    
    @field_validator("codigo")
    @classmethod
    def val_codigo(cls, v): return validate_codigo(v)
    
class DisciplinaCreate(DisciplinaModel):
    pass

class DisciplinaResponse(DisciplinaModel):
    id: UUID
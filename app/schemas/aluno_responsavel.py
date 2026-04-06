from uuid import UUID

from pydantic import BaseModel, field_validator
from app.validators.common_validator import not_empty

class AlunoResponsavelBase(BaseModel):
    fk_aluno: UUID
    fk_responsavel: UUID
    parentesco: str | None = None
    is_financeiro: bool = False
    tipo_responsavel: str = "PRIMARIO"
    
class AlunoResponsavelCreate(AlunoResponsavelBase):
    @field_validator('parentesco')
    @classmethod
    def val_parentesco_not_empty(cls, v): return not_empty(v)

class AlunoResponsavelResponse(AlunoResponsavelBase):
    model_config = {'from_attributes': True}
from pydantic import BaseModel, field_validator
from datetime import date
from uuid import UUID
from app.schemas.usuario import UsuarioResponse
from app.validators.funcionario_validator import (
    not_empty,
    validate_matricula
)

class FuncionarioModel(BaseModel):
    data_admissao: date
    matricula: str
    cargo: str
    
    @field_validator("matricula", "cargo")
    @classmethod
    def val_not_empty(cls, v): return not_empty(v)
    
    @field_validator("matricula")
    @classmethod
    def val_matricula(cls, v): return validate_matricula(v)
    
class FuncionarioCreate(FuncionarioModel):
    fk_usuario: UUID

class FuncionarioResponse(FuncionarioModel):
    id: UUID
    usuario: UsuarioResponse
    
    model_config = {'from_attributes': True}
from datetime import date
from uuid import UUID

from pydantic import BaseModel, field_validator

from app.schemas.turma import TurmaResponse
from app.schemas.usuario import UsuarioResponse
from app.validators.aluno_validator import validate_data_matricula, validate_matricula
from app.validators.common_validator import not_empty


class AlunoBase(BaseModel):
    matricula: str
    data_matricula: date
    
    @field_validator("matricula")
    @classmethod
    def val_not_empty(cls, v): return not_empty(v)
    
    @field_validator("matricula")
    @classmethod
    def val_matricula(cls, v): return validate_matricula(v)
    
    @field_validator("data_matricula")
    @classmethod
    def val_data_matricula(cls, v): return validate_data_matricula(v)
    
class AlunoCreate(AlunoBase):
    fk_turma: UUID
    fk_usuario: UUID

class AlunoResponse(AlunoBase):
    id: UUID
    turma: TurmaResponse
    usuario: UsuarioResponse
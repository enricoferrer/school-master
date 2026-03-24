from pydantic import BaseModel, EmailStr, field_validator
from datetime import date, datetime
from uuid import UUID
from app.validators.usuario_validator import (
    nome_social_strip,
    validate_cpf,
    validate_telefone,
    validate_data_nascimento,
)
from app.validators.common_validator import (
    not_empty
)

class UsuarioModel(BaseModel):
    nome_completo: str
    nome_social: str | None = None    
    data_nascimento: date
    cpf: str
    registro_geral: str
    fk_role: UUID
    genero: str
    email: EmailStr
    endereco: str
    telefone: str

class UsuarioCreate(UsuarioModel):
    senha_hash: str
    
    
    @field_validator("cpf")
    @classmethod
    def val_cpf(cls, v): return validate_cpf(v)

    @field_validator("telefone")
    @classmethod
    def val_telefone(cls, v): return validate_telefone(v)
    
        
    @field_validator("nome_completo", "registro_geral", "genero", "endereco")
    @classmethod
    def val_not_empty(cls, v): return not_empty(v)

    @field_validator("nome_social")
    @classmethod
    def val_nome_social(cls, v): return nome_social_strip(v)

    @field_validator("data_nascimento")
    @classmethod
    def val_data_nascimento(cls, v): return validate_data_nascimento(v)
    
class UsuarioResponse(UsuarioModel):
    id: UUID
    tentativas_falhas: int = 0
    bloqueado_ate: datetime | None = None
    is_active: bool = True
    criado_em: datetime | None = None
    atualizado_em: datetime | None = None
    
    model_config = {'from_attributes': True}
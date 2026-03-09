from pydantic import BaseModel, EmailStr
from datetime import date
from uuid import UUID

class UsuarioModel(BaseModel):
    nome_completo: str
    nome_social: str | None = None    
    data_nascimento: date
    cpf: str
    registro_geral: str
    genero: str
    email: EmailStr
    endereco: str
    telefone: str

class UsuarioCreate(UsuarioModel):
    pass
    
class UsuarioResponse(UsuarioModel):
    id: UUID
    
    model_config = {'from_attributes': True}
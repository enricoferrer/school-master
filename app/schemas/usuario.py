from pydantic import BaseModel, EmailStr
from datetime import date

class UsuarioModel(BaseModel):
    nome_completo: str
    nome_social: str
    data_nascimento: date
    cpf: str
    registro_geral: str
    genero: str
    email: EmailStr
    endereco: str

class UsuarioCreate(UsuarioModel):
    pass
    
class UsuarioResponse(UsuarioModel):
    id: str
    
    model_config = {'from_attributes': True}
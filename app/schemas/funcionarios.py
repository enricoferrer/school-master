from pydantic import BaseModel
from datetime import date
from uuid import UUID
from app.schemas.usuario import UsuarioResponse

class FuncionarioModel(BaseModel):
    data_admissao: date
    matricula: str
    cargo: str
    
class FuncionarioCreate(FuncionarioModel):
    fk_usuario: UUID

class FuncionarioResponse(FuncionarioModel):
    id: UUID
    usuario: UsuarioResponse
    
    model_config = {'from_attributes': True}
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from app.schemas.usuario import UsuarioResponse, UsuarioCreate
from app.core.database import get_db
from app.services.usuario_service import UsuarioService
from app.repositories.usuario_repository import UsuarioRepository
from sqlalchemy.orm import Session
from app.exceptions.NotFoundException import NotFoundException
from app.exceptions.DuplicateFieldException import DuplicateFieldException

router = APIRouter(prefix="/usuarios", tags=["Usuários"])

def get_service(db: Session = Depends(get_db)):
    return UsuarioService(UsuarioRepository(db))

@router.post("/", response_model=UsuarioResponse, status_code=201)
def create_usuario(data: UsuarioCreate, service: UsuarioService = Depends(get_service)):
    try:
        usuario = service.create(data)
        return usuario
    except DuplicateFieldException as e:
        raise HTTPException(409, detail=str(e))

@router.get("/", response_model=List[UsuarioResponse])
def list_usuarios(service: UsuarioService = Depends(get_service)):
    return service.list_usuarios()

@router.get("/{id}", response_model=UsuarioResponse)
def get_usuario_by_id(id: str, service: UsuarioService = Depends(get_service)):
    try:
        return service.get_usuario_by_id(id)
    except NotFoundException as e:
        raise HTTPException(404, detail=str(e))

@router.delete("/{id}", status_code=204)
def delete_usuario_by_id(id: str, service: UsuarioService = Depends(get_service)):
    service.delete_usuario_by_id(id)


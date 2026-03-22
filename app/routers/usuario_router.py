from typing import List

from fastapi import APIRouter, Depends, HTTPException
from app.dependencies.auth import require_permission
from app.schemas.usuario import UsuarioResponse, UsuarioCreate
from app.core.database import get_db
from app.services.usuario_service import UsuarioService
from app.repositories.usuario_repository import UsuarioRepository
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from app.exceptions.NotFoundException import NotFoundException
from app.exceptions.DuplicateFieldException import DuplicateFieldException

router = APIRouter(prefix="/usuarios", tags=["Usuários"])

def get_service(db: AsyncSession = Depends(get_db)):
    return UsuarioService(UsuarioRepository(db))

@router.post("/", response_model=UsuarioResponse, status_code=201)
async def create_usuario(data: UsuarioCreate, service: UsuarioService = Depends(get_service)):
    try:
        usuario = await service.create(data)
        return usuario
    except DuplicateFieldException as e:
        raise HTTPException(409, detail=str(e))

@router.get("/", response_model=List[UsuarioResponse], dependencies=[Depends(require_permission("user:read"))])
async def list_usuarios(service: UsuarioService = Depends(get_service)):
    return await service.list_usuarios()

@router.get("/{id}", response_model=UsuarioResponse, dependencies=[Depends(require_permission("user:read"))])
async def get_usuario_by_id(id: str, service: UsuarioService = Depends(get_service)):
    try:
        return await service.get_usuario_by_id(id)
    except NotFoundException as e:
        raise HTTPException(404, detail=str(e))

@router.delete("/{id}", status_code=204, dependencies=[Depends(require_permission("user:delete"))])
async def delete_usuario_by_id(id: str, service: UsuarioService = Depends(get_service)):
    await service.delete_usuario_by_id(id)


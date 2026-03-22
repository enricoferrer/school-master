from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.dependencies.auth import require_permission
from app.repositories.funcionario_repository import FuncionarioRepository
from app.services.funcionario_service import FuncionarioService
from app.schemas.funcionarios import FuncionarioCreate, FuncionarioResponse
from app.exceptions.NotFoundException import NotFoundException


router = APIRouter(prefix="/funcionarios", tags=["Funcionarios"])

def get_service(db: AsyncSession = Depends(get_db)):
    return FuncionarioService(FuncionarioRepository(db))

@router.post("/", response_model=FuncionarioResponse, status_code=201, dependencies=[Depends(require_permission("funcionario:write"))])
async def create_funcionario(data: FuncionarioCreate, service: FuncionarioService = Depends(get_service)):
    return await service.create(data)

@router.get("/", response_model=List[FuncionarioResponse], dependencies=[Depends(require_permission("funcionario:read"))])
async def list_funcionario(service: FuncionarioService = Depends(get_service)):
    return await service.list_funcionario()

@router.get("/{id}", response_model=FuncionarioResponse, dependencies=[Depends(require_permission("funcionario:read"))])
async def get_funcionario_by_id(id: UUID, service: FuncionarioService = Depends(get_service)):
    try:
        usuario = await service.get_funcionario_by_id(id)
        return usuario
    except NotFoundException as e:
        raise HTTPException(404, detail=str(e))
    
@router.delete("/{id}", status_code=204, dependencies=[Depends(require_permission("funcionario:write"))])
async def delete_funcionario_by_id(id: UUID, service: FuncionarioService = Depends(get_service)):
    await service.delete_funcionario(id)
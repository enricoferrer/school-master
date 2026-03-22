from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import require_permission
from app.exceptions.DuplicateEntityException import DuplicateEntityException
from app.exceptions.NotFoundException import NotFoundException
from app.repositories.turma_repository import TurmaRepository
from app.schemas.turma import TurmaCreate, TurmaResponse
from app.services.turma_service import TurmaService


router = APIRouter(prefix="/turma", tags=["Turmas"])

def get_service(db: AsyncSession = Depends(get_db)):
    return TurmaService(TurmaRepository(db))

@router.post("/", response_model=TurmaResponse, status_code=201, dependencies=[Depends(require_permission("aluno:write"))])
async def create(data: TurmaCreate, service: TurmaService = Depends(get_service)):
    try:
        turma = await service.create(data)
        return turma
    except DuplicateEntityException as e:
        raise HTTPException(409, detail=str(e))
    
@router.get("/", response_model=list[TurmaResponse], dependencies=[Depends(require_permission("aluno:read"))])
async def list_turmas(service: TurmaService = Depends(get_service)):
    return await service.list_turmas()

@router.get("/{id}", response_model=TurmaResponse, dependencies=[Depends(require_permission("aluno:read"))])
async def get_turma_by_id(id: UUID, service: TurmaService = Depends(get_service)):
    try:
        turma = await service.get_turma_by_id(id)
        return turma
    except NotFoundException as e:
        raise HTTPException(404, detail=str(e))

@router.delete("/{id}", status_code=204, dependencies=[Depends(require_permission("aluno:write"))])
async def delete_turma_by_id(id: UUID, service: TurmaService = Depends(get_service)):
    try:
        await service.delete_turma_by_id(id)
    except NotFoundException as e:
        raise HTTPException(404, detail=str(e))
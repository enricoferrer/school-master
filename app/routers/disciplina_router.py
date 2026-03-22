from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from app.core.database import get_db
from app.dependencies.auth import require_permission
from app.schemas.disciplina import DisciplinaCreate, DisciplinaResponse
from app.repositories.disciplina_repository import DisciplinaRepository
from app.services.disciplina_service import DisciplinaService
from sqlalchemy.ext.asyncio import AsyncSession
from app.exceptions.NotFoundException import NotFoundException
from app.exceptions.DuplicateFieldException import DuplicateFieldException

router = APIRouter(prefix="/disciplinas", tags=["Disciplina"])

def get_service(db: AsyncSession = Depends(get_db)):
    return DisciplinaService(DisciplinaRepository(db))

@router.post("/", response_model=DisciplinaResponse, status_code=201, dependencies=[Depends(require_permission("grade:write"))])
async def create_disciplina(data: DisciplinaCreate, service: DisciplinaService = Depends(get_service)):
    try:
        disciplina = await service.create(data)
        return disciplina
    except DuplicateFieldException as e:
        raise HTTPException(409, detail=str(e))

@router.get("/", response_model=List[DisciplinaResponse], dependencies=[Depends(require_permission("grade:read"))])
async def list_disciplina(service: DisciplinaService = Depends(get_service)):
    return await service.list_disciplina()

@router.get("/{id}", response_model=DisciplinaResponse, dependencies=[Depends(require_permission("grade:read"))])
async def get_disciplina_by_id(id: UUID, service: DisciplinaService = Depends(get_service)):
    try:
        disciplina = await service.get_disciplina_by_id(id)
        return disciplina
    except NotFoundException as e:
        raise HTTPException(404, detail=str(e))

@router.delete("/{id}", status_code=204, dependencies=[Depends(require_permission("grade:write"))])
async def delete_disciplina_by_id(id: UUID, service: DisciplinaService = Depends(get_service)):
    await service.delete_disciplina_by_id(id)
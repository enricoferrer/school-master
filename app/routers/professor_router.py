from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from app.core.database import get_db
from app.dependencies.auth import require_permission
from app.repositories.professor_repository import ProfessorRepository
from app.services.professor_service import ProfessorService
from app.schemas.professor import ProfessorCreate, ProfessorResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.exceptions.NotFoundException import NotFoundException

router = APIRouter(prefix="/professor", tags=["Professor"])

def get_service(db: AsyncSession = Depends(get_db)):
    return ProfessorService(ProfessorRepository(db))

@router.post("/", response_model=ProfessorResponse, status_code=201, dependencies=[Depends(require_permission("funcionario:write"))])
async def create_professor(data: ProfessorCreate, service: ProfessorService = Depends(get_service)):
    return await service.create(data)

@router.get("/", response_model=List[ProfessorResponse], dependencies=[Depends(require_permission("funcionario:read"))])
async def list_professor(service: ProfessorService = Depends(get_service)):
    return await service.list_professor()

@router.get("/{id}", response_model=ProfessorResponse, dependencies=[Depends(require_permission("funcionario:read"))])
async def get_professor_by_id(id: UUID,service: ProfessorService = Depends(get_service)):
    try:
        professor = await service.get_professor_by_id(id)
        return professor
    except NotFoundException as e:
        raise HTTPException(404, detail=str(e))
        
@router.delete("{/id}", status_code=204, dependencies=[Depends(require_permission("funcionario:write"))])
async def delete_professor_by_id(id: UUID, service: ProfessorService = Depends(get_service)):
    await service.delete_professor_by_id(id)
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from app.core.database import get_db
from app.dependencies.auth import require_permission
from app.repositories.professor_disciplina_repository import ProfessorDisciplinaRepository
from app.services.professor_disciplina_service import ProfessorDisciplinaService
from app.schemas.professor_disciplina import ProfessorDisciplinaCreate, ProfessorDisciplinaResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.exceptions.DuplicateEntityException import DuplicateEntityException
from app.exceptions.NotFoundException import NotFoundException

router = APIRouter(prefix="/professor-disciplina", tags=["Professor-Disciplina"])

def get_service(db: AsyncSession = Depends(get_db)):
    return ProfessorDisciplinaService(ProfessorDisciplinaRepository(db))

@router.post("/", response_model=ProfessorDisciplinaResponse, status_code=201, dependencies=[Depends(require_permission("funcionario:write"))])
async def create(data: ProfessorDisciplinaCreate, service: ProfessorDisciplinaService = Depends(get_service)):
    try:
        vinculo = await service.create(data)
        return vinculo
    except DuplicateEntityException as e:
        raise HTTPException(409, detail=str(e))
    
@router.get("/id-professor", response_model=list[ProfessorDisciplinaResponse], dependencies=[Depends(require_permission("funcionario:read"))])
async def get_disciplinas_do_professor(id_professor: UUID, service: ProfessorDisciplinaService = Depends(get_service)):
    try:
        vinculos = await service.list_disciplinas_do_professor(id_professor)
        return vinculos
    except NotFoundException as e:
        raise HTTPException(404,detail=str(e))

@router.get("/id-disciplina", response_model=list[ProfessorDisciplinaResponse], dependencies=[Depends(require_permission("funcionario:read"))])
async def get_disciplinas_do_professor(id_disciplina: UUID, service: ProfessorDisciplinaService = Depends(get_service)):
    try:
        vinculos = await service.list_professores_da_disciplina(id_disciplina)
        return vinculos
    except NotFoundException as e:
        raise HTTPException(404,detail=str(e))
    
@router.get("/vinculo", response_model=ProfessorDisciplinaResponse, dependencies=[Depends(require_permission("funcionario:read"))])
async def get_vinculo(id_disciplina: UUID, id_professor: UUID, service: ProfessorDisciplinaService = Depends(get_service)):
    try:
        vinculo = await service.get_vinculo(id_disciplina, id_professor)
        return vinculo
    except NotFoundException as e:
        raise HTTPException(404, detail=str(e))
    
@router.delete("/vinculo", status_code=204, dependencies=[Depends(require_permission("funcionario:write"))])
async def delete_vinculo(id_disciplina: UUID, id_professor: UUID, service: ProfessorDisciplinaService = Depends(get_service)):
    try:
        await service.delete_vinculo(id_professor, id_disciplina)
    except NotFoundException as e:
        raise HTTPException(404, detail=str(e))
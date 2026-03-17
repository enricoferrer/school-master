from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from app.core.database import get_db
from app.repositories.professor_disciplina_repository import ProfessorDisciplinaRepository
from app.services.professor_disciplina_service import ProfessorDisciplinaService
from app.schemas.professor_disciplina import ProfessorDisciplinaCreate, ProfessorDisciplinaResponse
from sqlalchemy.orm import Session
from app.exceptions.DuplicateEntityException import DuplicateEntityException
from app.exceptions.NotFoundException import NotFoundException

router = APIRouter(prefix="/professor-disciplina", tags=["Professor-Disciplina"])

def get_service(db: Session = Depends(get_db)):
    return ProfessorDisciplinaService(ProfessorDisciplinaRepository(db))

@router.post("/", response_model=ProfessorDisciplinaResponse, status_code=201)
def create(data: ProfessorDisciplinaCreate, service: ProfessorDisciplinaService = Depends(get_service)):
    try:
        vinculo = service.create(data)
        return vinculo
    except DuplicateEntityException as e:
        raise HTTPException(409, detail=str(e))
    
@router.get("/id-professor", response_model=list[ProfessorDisciplinaResponse])
def get_disciplinas_do_professor(id_professor: UUID, service: ProfessorDisciplinaService = Depends(get_service)):
    try:
        vinculos = service.list_disciplinas_do_professor(id_professor)
        return vinculos
    except NotFoundException as e:
        raise HTTPException(404,detail=str(e))

@router.get("/id-disciplina", response_model=list[ProfessorDisciplinaResponse])
def get_disciplinas_do_professor(id_disciplina: UUID, service: ProfessorDisciplinaService = Depends(get_service)):
    try:
        vinculos = service.list_professores_da_disciplina(id_disciplina)
        return vinculos
    except NotFoundException as e:
        raise HTTPException(404,detail=str(e))
    
@router.get("/vinculo", response_model=ProfessorDisciplinaResponse)
def get_vinculo(id_disciplina: UUID, id_professor: UUID, service: ProfessorDisciplinaService = Depends(get_service)):
    try:
        vinculo = service.get_vinculo(id_disciplina, id_professor)
        return vinculo
    except NotFoundException as e:
        raise HTTPException(404, detail=str(e))
    
@router.delete("/vinculo", status_code=204)
def delete_vinculo(id_disciplina: UUID, id_professor: UUID, service: ProfessorDisciplinaService = Depends(get_service)):
    try:
        service.delete_vinculo(id_professor, id_disciplina)
    except NotFoundException as e:
        raise HTTPException(404, detail=str(e))
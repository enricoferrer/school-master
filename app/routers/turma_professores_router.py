from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.exceptions.DuplicateEntityException import DuplicateEntityException
from app.exceptions.NotFoundException import NotFoundException
from app.repositories.turma_professores_repository import TurmaProfessoresRepository
from app.schemas.turma_professores import TurmaProfessoresCreate, TurmaProfessoresResponse
from app.services.turma_professores_service import TurmaProfessoresService


router = APIRouter(prefix="/turma-professores", tags=["Turma-Professores"])

def get_service(db: Session = Depends(get_db)):
    return TurmaProfessoresService(TurmaProfessoresRepository(db))

@router.post("/", response_model=TurmaProfessoresResponse, status_code=201)
def create(data: TurmaProfessoresCreate, service: TurmaProfessoresService = Depends(get_service)):
    try:
        vinculo = service.create(data)
        return vinculo
    except DuplicateEntityException as e:
        raise HTTPException(409, detail=str(e))
    
@router.get("/id-professor", response_model=List[TurmaProfessoresResponse])
def list_turmas_do_professor(id_professor: UUID, service: TurmaProfessoresService = Depends(get_service)):
    try:
        turmas = service.list_turmas_do_professor(id_professor)
        return turmas
    except NotFoundException as e:
        raise HTTPException(404, detail=str(e))
    
@router.get("/id-turma", response_model=List[TurmaProfessoresResponse])
def list_professores_da_turma(id_turma: UUID, service: TurmaProfessoresService = Depends(get_service)):
    try:
        professores = service.list_professores_da_turma(id_turma)
        return professores
    except NotFoundException as e:
        raise HTTPException(404, detail=str(e))
    
@router.delete("/vinculo", status_code=204)
def delete_vinculo(id_professor: UUID, id_turma: UUID, id_disciplina: UUID, service: TurmaProfessoresService = Depends(get_service)):
    try:
        service.delete_vinculo_by_id(id_turma, id_professor, id_disciplina)
    except NotFoundException as e:
        raise HTTPException(404, detail=str(e))
    
@router.get("/{id}", response_model=TurmaProfessoresResponse)
def get_vinculo_by_id(id: UUID, service: TurmaProfessoresService = Depends(get_service)):
    try:
        vinculo = service.get_vinculo_by_id(id)
        return vinculo
    except NotFoundException as e:
        raise HTTPException(404, detail=str(e))
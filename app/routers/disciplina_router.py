from email.policy import default
from http.client import HTTPException
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends
from app.core.database import get_db
from app.schemas.disciplina import DisciplinaCreate, DisciplinaResponse
from app.repositories.disciplina_repository import DisciplinaRepository
from app.services.disciplina_service import DisciplinaService
from sqlalchemy.orm import Session
from app.exceptions import NotFoundException

router = APIRouter(prefix="/disciplinas", tags=["Disciplina"])

def get_service(db: Session = Depends(get_db)):
    return DisciplinaService(DisciplinaRepository(db))

@router.post("/", response_model=DisciplinaResponse, status_code=201)
def create_disciplina(data: DisciplinaCreate, service: DisciplinaService = Depends(get_service)):
    return service.create(data)

@router.get("/", response_model=List[DisciplinaResponse])
def list_disciplina(service: DisciplinaService = Depends(get_service)):
    return service.list_disciplina()

@router.get("/{id}", response_model=DisciplinaResponse)
def get_disciplina_by_id(id: UUID, service: DisciplinaService = Depends(get_service)):
    try:
        disciplina = service.get_disciplina_by_id(id)
        return disciplina
    except NotFoundException as e:
        raise HTTPException(404, detail=str(e))

@router.delete("/{id}", status_code=204)
def delete_disciplina_by_id(id: UUID, service: DisciplinaService = Depends(get_service)):
    service.delete_disciplina_by_id(id)
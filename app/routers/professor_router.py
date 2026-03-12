from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from app.core.database import get_db
from app.repositories.professor_repository import ProfessorRepository
from app.services.professor_service import ProfessorService
from app.schemas.professor import ProfessorCreate, ProfessorResponse
from sqlalchemy.orm import Session
from app.exceptions import NotFoundException

router = APIRouter(prefix="/professor", tags=["Professor"])

def get_service(db: Session = Depends(get_db)):
    return ProfessorService(ProfessorRepository(db))

@router.post("/", response_model=ProfessorResponse, status_code=201)
def create_professor(data: ProfessorCreate, service: ProfessorService = Depends(get_service)):
    return service.create(data)

@router.get("/", response_model=List[ProfessorResponse])
def list_professor(service: ProfessorService = Depends(get_service)):
    return service.list_professor()

@router.get("/{id}", response_model=ProfessorResponse)
def get_professor_by_id(id: UUID,service: ProfessorService = Depends(get_service)):
    try:
        professor = service.get_professor_by_id(id)
        return professor
    except NotFoundException as e:
        raise HTTPException(404, detail=str(e))
        
@router.delete("{/id}", status_code=204)
def delete_professor_by_id(id: UUID, service: ProfessorService = Depends(get_service)):
    service.delete_professor_by_id(id)
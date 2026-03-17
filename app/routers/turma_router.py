from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from passlib import exc
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.exceptions.DuplicateEntityException import DuplicateEntityException
from app.exceptions.NotFoundException import NotFoundException
from app.repositories.turma_repository import TurmaRepository
from app.schemas.turma import TurmaCreate, TurmaResponse
from app.services.turma_service import TurmaService


router = APIRouter(prefix="/turma", tags=["Turmas"])

def get_service(db: Session = Depends(get_db)):
    return TurmaService(TurmaRepository(db))

@router.post("/", response_model=TurmaResponse, status_code=201)
def create(data: TurmaCreate, service: TurmaService = Depends(get_service)):
    try:
        turma = service.create(data)
        return turma
    except DuplicateEntityException as e:
        raise HTTPException(409, detail=str(e))
    
@router.get("/", response_model=list[TurmaResponse])
def list_turmas(service: TurmaService = Depends(get_service)):
    return service.list_turmas()

@router.get("/{id}", response_model=TurmaResponse)
def get_turma_by_id(id: UUID, service: TurmaService = Depends(get_service)):
    try:
        turma = service.get_turma_by_id(id)
        return turma
    except NotFoundException as e:
        HTTPException(404, detail=str(e))
        
@router.delete("/{id}", status_code=204)
def delete_turma_by_id(id: UUID, service: TurmaService = Depends(get_service)):
    try:
        turma = service.delete_turma_by_id(id)
    except NotFoundException as e:
        raise HTTPException(404, detail=str(e))
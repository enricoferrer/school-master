from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from passlib import exc
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.exceptions.DuplicateFieldException import DuplicateFieldException
from app.exceptions.NotFoundException import NotFoundException
from app.repositories.aluno_repository import AlunoRepository
from app.schemas.aluno import AlunoCreate, AlunoResponse
from app.services.aluno_service import AlunoService


router = APIRouter(prefix="/alunos", tags=["Alunos"])

def get_service(db: Session = Depends(get_db)):
    return AlunoService(AlunoRepository(db))

@router.post("/", response_model=AlunoResponse, status_code=201)
def create(data: AlunoCreate, service: AlunoService = Depends(get_service)):
    try:
        aluno = service.create(data)
        return aluno
    except DuplicateFieldException as e:
        raise HTTPException(409, detail=str(e))
    
@router.get("/", response_model=List[AlunoResponse])    
def list_alunos(matricula: str = None, service: AlunoService = Depends(get_service)):
    if matricula:
        try:
            aluno = service.get_aluno_by_matricula(matricula)
            return [aluno]
        except NotFoundException as e:
            raise HTTPException(404, detail=str(e))
    return service.list_alunos()

@router.get("/{id}", response_model=AlunoResponse)
def get_aluno_by_id(id: UUID, service: AlunoService = Depends(get_service)):
    try:
        aluno = service.get_aluno_by_id(id)
        return aluno
    except NotFoundException as e:
        raise HTTPException(404, detail=str(e))
    
@router.delete("/{id}", status_code=204)
def delete_aluno_by_id(id: UUID, service: AlunoService = Depends(get_service)):
    try:
        service.delete_aluno_by_id(id)
    except NotFoundException as e:
        raise HTTPException(404, detail=str(e))
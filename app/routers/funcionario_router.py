from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.repositories.funcionario_repository import FuncionarioRepository
from app.services.funcionario_service import FuncionarioService
from app.schemas.funcionarios import FuncionarioCreate, FuncionarioResponse
from app.exceptions.NotFoundException import NotFoundException


router = APIRouter(prefix="/funcionarios", tags=["Funcionarios"])

def get_service(db: Session = Depends(get_db)):
    return FuncionarioService(FuncionarioRepository(db))

@router.post("/", response_model=FuncionarioResponse, status_code=201)
def create_funcionario(data: FuncionarioCreate, service: FuncionarioService = Depends(get_service)):
    return service.create(data)

@router.get("/", response_model=List[FuncionarioResponse])
def list_funcionario(service: FuncionarioService = Depends(get_service)):
    return service.list_funcionario()

@router.get("/{id}", response_model=FuncionarioResponse)
def get_funcionario_by_id(id: UUID, service: FuncionarioService = Depends(get_service)):
    try:
        usuario = service.get_funcionario_by_id(id)
        return usuario
    except NotFoundException as e:
        raise HTTPException(404, detail=str(e))
    
@router.delete("/{id}", status_code=204)
def delete_funcionario_by_id(id: UUID, service: FuncionarioService = Depends(get_service)):
    service.delete_funcionario(id)
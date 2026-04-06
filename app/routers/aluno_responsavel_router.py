from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from httpx import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.exceptions.DuplicateEntityException import DuplicateEntityException
from app.exceptions.NotFoundException import NotFoundException
from app.repositories.aluno_repository import AlunoRepository
from app.repositories.aluno_responsavel_repository import AlunoResponsavelRepository
from app.repositories.usuario_repository import UsuarioRepository
from app.schemas.aluno_responsavel import AlunoResponsavelCreate, AlunoResponsavelResponse
from app.services.aluno_responsavel_service import AlunoResponsavelService

router = APIRouter(prefix="/responsaveis", tags=["Responsaveis de Alunos"])

def get_service(db: AsyncSession = Depends(get_db)):
    return AlunoResponsavelService(
        AlunoResponsavelRepository(db), 
        AlunoRepository(db), 
        UsuarioRepository(db)
        )
    
@router.post("/", response_model=AlunoResponsavelResponse, status_code=201)
async def criar_vinculo(data: AlunoResponsavelCreate, service: AlunoResponsavelService = Depends(get_service)):
    try:
        return await service.create(data)
    except NotFoundException as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e))
    except DuplicateEntityException as e:
        raise HTTPException(status.HTTP_409_CONFLICT, str(e))
    
@router.get("/{fk_aluno}", response_model=list[AlunoResponsavelResponse])
async def list_responsaveis_by_aluno(fk_aluno: UUID, service: AlunoResponsavelService = Depends(get_service)):
    try:
        return await service.list_responsaveis_by_aluno(fk_aluno)
    except NotFoundException as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e))

@router.get("/{fk_aluno}/{fk_responsavel}", response_model=AlunoResponsavelResponse)
async def get_vinculo(fk_aluno: UUID, fk_responsavel: UUID, service: AlunoResponsavelService = Depends(get_service)):
    try:
        return await service.get_responsavel_by_id(fk_aluno, fk_responsavel)
    except NotFoundException as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e))
   
@router.delete("/{fk_aluno}/{fk_responsavel}", status_code=204) 
async def delete_vinculo(fk_aluno: UUID, fk_responsavel: UUID, service: AlunoResponsavelService = Depends(get_service)):
    try:
        await service.delete(fk_aluno, fk_responsavel)
    except NotFoundException as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e))
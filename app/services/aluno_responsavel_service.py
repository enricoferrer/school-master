from uuid import UUID

from app.exceptions.DuplicateEntityException import DuplicateEntityException
from app.exceptions.NotFoundException import NotFoundException
from app.models.aluno_responsavel import AlunoResponsavel
from app.repositories.aluno_repository import AlunoRepository
from app.repositories.aluno_responsavel_repository import AlunoResponsavelRepository
from app.repositories.usuario_repository import UsuarioRepository
from app.schemas.aluno_responsavel import AlunoResponsavelCreate


class AlunoResponsavelService:
    def __init__(self, repository: AlunoResponsavelRepository, aluno_repository: AlunoRepository, usuario_repository: UsuarioRepository):
        self.repository = repository
        self.aluno_repository = aluno_repository
        self.usuario_repository = usuario_repository

    async def create(self, data: AlunoResponsavelCreate):
        if not await self._validar_aluno_existe(data.fk_aluno):
            raise NotFoundException("Aluno não encontrado")
        if not await self._validar_responsavel_existe(data.fk_responsavel):
            raise NotFoundException("Responsável não encontrado")
        if await self._validar_vinculo_existe(data.fk_aluno, data.fk_responsavel):
            raise DuplicateEntityException("Vínculo entre aluno e responsável já existe")
        return await self.repository.create(data)
    
    async def get_responsavel_by_id(self, fk_aluno: UUID, fk_responsavel: UUID):
        responsavel = await self.repository.search_responsavel_by_id(fk_aluno, fk_responsavel)
        if not responsavel:
            raise NotFoundException("Vínculo entre aluno e responsável não encontrado")
        return responsavel
    
    async def list_responsaveis_by_aluno(self, fk_aluno: UUID) -> list[AlunoResponsavel]:
        if not await self._validar_aluno_existe(fk_aluno):
            raise NotFoundException("Aluno não encontrado")
        return await self.repository.list_responsaveis_by_aluno(fk_aluno)
    
    async def delete(self, fk_aluno: UUID, fk_responsavel: UUID):
        if not await self._validar_vinculo_existe(fk_aluno, fk_responsavel):
            raise NotFoundException("Vínculo entre aluno e responsável não encontrado")
        await self.repository.delete(fk_aluno, fk_responsavel)
    
    async def _validar_aluno_existe(self, aluno_id: UUID) -> bool:
        aluno_existe = await self.aluno_repository.get_aluno_by_id(aluno_id)
        return bool(aluno_existe) 
    
    async def _validar_responsavel_existe(self, responsavel_id: UUID) -> bool:
        responsavel_existe = await self.usuario_repository.get_usuario_by_id(responsavel_id)
        return bool(responsavel_existe)
    
    async def _validar_vinculo_existe(self, fk_aluno: UUID, fk_responsavel: UUID) -> bool:
        vinculo_existe = await self.repository.search_responsavel_by_id(fk_aluno, fk_responsavel)
        return bool(vinculo_existe)
        
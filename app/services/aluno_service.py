from uuid import UUID

from app.exceptions import DuplicateFieldException
from app.exceptions.NotFoundException import NotFoundException
from app.repositories.aluno_repository import AlunoRepository
from app.schemas.aluno import AlunoCreate, AlunoUpdate


class AlunoService:
    def __init__(self, repository: AlunoRepository):
        self.repository = repository
        
    async def create(self, data: AlunoCreate):
        matricula_existe = await self.repository.get_aluno_by_matricula(data.matricula)
        if matricula_existe:
            raise DuplicateFieldException("Um aluno com essa matricula já existe!")
        return await self.repository.create(data)
    
    async def list_alunos(self):
        return await self.repository.list_alunos()
    
    async def get_aluno_by_id(self, id: UUID):
        aluno = await self.repository.get_aluno_by_id(id)
        if not aluno:
            raise NotFoundException("Aluno com esse ID não foi encontrado")
        return aluno
    
    async def delete_aluno_by_id(self, id: UUID):
        aluno = await self.repository.get_aluno_by_id(id)
        if not aluno:
            raise NotFoundException("Aluno com esse ID não foi encontrado")
        await self.repository.delete_aluno(aluno)
        
    async def get_aluno_by_matricula(self, matricula: str):
        aluno = await self.repository.get_aluno_by_matricula(matricula)
        if not aluno:
            raise NotFoundException("Aluno com essa matricula não foi encontrado")
        return aluno
    
    async def update_turma_aluno(self, data_atualizar: AlunoUpdate):
        aluno = await self.repository.insert_aluno_turma(data_atualizar)
        if not aluno:
            raise NotFoundException("Aluno não foi encontrado")
        return aluno
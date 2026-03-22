from uuid import UUID

from app.repositories.disciplina_repository import DisciplinaRepository
from app.schemas.disciplina import DisciplinaCreate
from app.exceptions import NotFoundException
from app.exceptions.DuplicateFieldException import DuplicateFieldException

class DisciplinaService:
    def __init__(self, repository: DisciplinaRepository):
        self.repository = repository
    
    async def create(self, data: DisciplinaCreate):
        disciplina_existente = await self.repository.get_disciplina_by_codigo(data.codigo)
        if disciplina_existente:
            raise DuplicateFieldException(f"Disciplina com o código '{data.codigo}' já existe!")
        return await self.repository.create(data)
    
    async def list_disciplina(self):
        return await self.repository.list_disciplina()
    
    async def get_disciplina_by_id(self, id: UUID):
        disciplina = await self.repository.get_disciplina_by_id(id)
        if disciplina is None:
            raise NotFoundException(f"Disciplina com o ID: '{id}' não foi encontrada!")
        return disciplina
    
    async def delete_disciplina_by_id(self, id: UUID):
        disciplina = await self.get_disciplina_by_id(id)
        await self.repository.delete_disciplina(disciplina)
from app.repositories.professor_repository import ProfessorRepository
from app.schemas.professor import ProfessorCreate
from app.exceptions import NotFoundException
from uuid import UUID

class ProfessorService:
    def __init__(self, repository: ProfessorRepository):
        self.repository = repository
        
    async def create(self, data: ProfessorCreate):
        return await self.repository.create(data)
    
    async def list_professor(self):
        return await self.repository.list_all_professor()
    
    async def get_professor_by_id(self, id: UUID):
        professor = await self.repository.get_professor_by_id(id)
        
        if professor is None:
            raise NotFoundException(f"Professor com o ID: '{id}' não foi encontrado!")
        
        return professor
    
    async def delete_professor_by_id(self, id: UUID):
        professor = await self.get_professor_by_id(id)
        await self.repository.delete_professor(professor)
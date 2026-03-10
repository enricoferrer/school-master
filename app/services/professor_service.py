from app.repositories.professor_repository import ProfessorRepository
from app.schemas.professor import ProfessorCreate
from app.exceptions import NotFoundException
from uuid import UUID

class ProfessorService:
    def __init__(self, repository: ProfessorRepository):
        self.repository = repository
        
    def create(self, data: ProfessorCreate):
        return self.repository.create(data)
    
    def list_professor(self):
        return self.repository.list_all_professor()
    
    def get_professor_by_id(self, id: UUID):
        professor = self.repository.get_professor_by_id(id)
        
        if professor is None:
            raise NotFoundException(f"Professor com o ID: '{id}' não foi encontrado!")
        
        return professor
    
    def delete_professor_by_id(self, id: UUID):
        professor = self.get_professor_by_id(id)
        self.repository.delete_professor(professor)
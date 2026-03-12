from uuid import UUID

from app.repositories.disciplina_repository import DisciplinaRepository
from app.schemas.disciplina import DisciplinaCreate
from app.exceptions import NotFoundException
from app.exceptions.DuplicateFieldException import DuplicateFieldException

class DisciplinaService:
    def __init__(self, repository: DisciplinaRepository):
        self.repository = repository
    
    def create(self, data: DisciplinaCreate):
        disciplina_existente = self.repository.get_disciplina_by_codigo(data.codigo)
        if disciplina_existente:
            raise DuplicateFieldException(f"Disciplina com o código '{data.codigo}' já existe!")
        return self.repository.create(data)
    
    def list_disciplina(self):
        return self.repository.list_disciplina()
    
    def get_disciplina_by_id(self, id: UUID):
        disciplina = self.repository.get_disciplina_by_id(id)
        if disciplina is None:
            raise NotFoundException(f"Disciplina com o ID: '{id}' não foi encontrada!")
        return disciplina
    
    def delete_disciplina_by_id(self, id: UUID):
        disciplina = self.get_disciplina_by_id(id)
        self.repository.delete_disciplina(disciplina)
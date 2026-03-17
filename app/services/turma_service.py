from uuid import UUID

from app.exceptions.DuplicateEntityException import DuplicateEntityException
from app.exceptions.NotFoundException import NotFoundException
from app.repositories.turma_repository import TurmaRepository
from app.schemas.turma import TurmaCreate


class TurmaService:
    def __init__(self, repository: TurmaRepository):
        self.repository = repository
        
    def create(self, data: TurmaCreate):
        turma_existe = self.repository.turma_existe(data.sala, data.serie)
        
        if turma_existe:
            raise DuplicateEntityException("Essa turma já está cadastrada")
        return self.repository.create(data)
    
    def list_turmas(self):
        return self.repository.list_turmas()
    
    def get_turma_by_id(self, id: UUID):
        turma = self.repository.get_turma_by_id(id)
        if not turma:
            raise NotFoundException("Turma não encontrada com esses parametros")
        return turma
    
    def delete_turma_by_id(self, id: UUID):
        turma = self.repository.get_turma_by_id(id)
        if not turma:
            raise NotFoundException("Turma não encontrada com esses parametros")
        self.repository.delete_turma(turma)
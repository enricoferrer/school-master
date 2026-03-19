from uuid import UUID

from app.exceptions.DuplicateEntityException import DuplicateEntityException
from app.exceptions.NotFoundException import NotFoundException
from app.repositories.turma_professores_repository import TurmaProfessoresRepository
from app.schemas.turma_professores import TurmaProfessoresCreate


class TurmaProfessoresService:
    def __init__(self, repository: TurmaProfessoresRepository):
        self.repository = repository
        
    def create(self, data: TurmaProfessoresCreate):
        vinculo_existe = self.repository.vinculo_ja_existe(data.fk_turma, data.fk_professor, data.fk_disciplina)
        if vinculo_existe:
            raise DuplicateEntityException("Esse professor já leciona essa disciplina nessa turma")
        return self.repository.create(data)
        
    def list_turmas_do_professor(self, id_professor: UUID):
        turmas = self.repository.list_turmas_do_professor(id_professor)
        if not turmas:
            raise NotFoundException("Esse professor não está lecionando em nenhuma turma!")
        return turmas
    
    def list_professores_da_turma(self, id_turma: UUID):
        professores = self.repository.list_professores_da_turma(id_turma)
        if not professores:
            raise NotFoundException("Essa turma não possui nenhum professor!")
        return professores
    
    def get_vinculo_by_id(self, id: UUID):
        vinculo = self.repository.get_vinculo_by_id(id)
        if not vinculo:
            raise NotFoundException("Nenhum vinculo encontrado com esse ID!")
        return vinculo
    
    def delete_vinculo_by_id(self, id_turma: UUID, id_professor: UUID, id_disciplina: UUID):
        vinculo = self.repository.get_vinculo(id_turma, id_professor, id_disciplina)
        if not vinculo:
            raise NotFoundException("Nenhum vinculo encontrado com esse ID!")
        self.repository.delete_vinculo(vinculo)
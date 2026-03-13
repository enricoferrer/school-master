from app.repositories.professor_disciplina_repository import ProfessorDisciplinaRepository
from app.schemas.professor_disciplina import ProfessorDisciplinaCreate
from uuid import UUID
from app.exceptions.DuplicateEntityException import DuplicateEntityException
from app.exceptions.EntityNotFoundException import EntityNotFoundException

class ProfessorDisciplinaService:
    def __init__(self, repository: ProfessorDisciplinaRepository):
        self.repository = repository
        
    def create(self, data: ProfessorDisciplinaCreate):
        vinculo_existente = self.repository.vinculo_existe(data.fk_disciplina, data.fk_professor)
        if vinculo_existente:
            raise DuplicateEntityException("Esse vínculo entre professor e disciplina já existe!")
        return self.repository.create(data)
    
    def list_disciplinas_do_professor(self, fk_professor: UUID):
        vinculos = self.repository.list_disciplinas_do_professor(fk_professor)
        if not vinculos:
            raise EntityNotFoundException("Vínculos não encontrado com os parametros disponibilizados")
        return vinculos
    
    def list_professores_da_disciplina(self, fk_disciplina: UUID):
        vinculos = self.repository.list_professores_da_disciplina(fk_disciplina)
        if not vinculos:
            raise EntityNotFoundException("Vínculos não encontrado com os parametros disponibilizados")
        return vinculos 
    
    def delete_vinculo(self, fk_professor: UUID, fk_disciplina: UUID):
        vinculo = self.repository.get_vinculo(fk_disciplina, fk_professor)
        if not vinculo:
            raise EntityNotFoundException("Vínculo não encontrado com os parametros disponibilizados")
        self.repository.delete_vinculo(vinculo)
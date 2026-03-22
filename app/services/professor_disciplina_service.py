from app.repositories.professor_disciplina_repository import ProfessorDisciplinaRepository
from app.schemas.professor_disciplina import ProfessorDisciplinaCreate
from uuid import UUID
from app.exceptions.DuplicateEntityException import DuplicateEntityException
from app.exceptions.NotFoundException import NotFoundException

class ProfessorDisciplinaService:
    def __init__(self, repository: ProfessorDisciplinaRepository):
        self.repository = repository
        
    async def create(self, data: ProfessorDisciplinaCreate):
        vinculo_existente = await self.repository.vinculo_existe(data.fk_disciplina, data.fk_professor)
        if vinculo_existente:
            raise DuplicateEntityException("Esse vínculo entre professor e disciplina já existe!")
        return await self.repository.create(data)
    
    async def list_disciplinas_do_professor(self, fk_professor: UUID):
        vinculos = await self.repository.list_disciplinas_do_professor(fk_professor)
        if not vinculos:
            raise NotFoundException("Vínculos não encontrado com os parametros disponibilizados")
        return vinculos
    
    async def list_professores_da_disciplina(self, fk_disciplina: UUID):
        vinculos = await self.repository.list_professores_da_disciplina(fk_disciplina)
        if not vinculos:
            raise NotFoundException("Vínculos não encontrado com os parametros disponibilizados")
        return vinculos 
    
    async def delete_vinculo(self, fk_professor: UUID, fk_disciplina: UUID):
        vinculo = await self.repository.get_vinculo(fk_disciplina, fk_professor)
        if not vinculo:
            raise NotFoundException("Vínculo não encontrado com os parametros disponibilizados")
        await self.repository.delete_vinculo(vinculo)
    
    async def vinculo_existe(self, fk_disciplina: UUID, fk_professor: UUID) -> bool:
        return await self.repository.vinculo_existe(fk_disciplina, fk_professor)
    
    async def get_vinculo(self, fk_disciplina: UUID, fk_professor: UUID):
        vinculo = await self.repository.get_vinculo(fk_disciplina, fk_professor)
        if not vinculo:
            raise NotFoundException("Vínculo não encontrado com os parametros disponibilizados")
        return vinculo
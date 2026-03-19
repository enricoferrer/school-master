from uuid import UUID

from app.exceptions import DuplicateFieldException
from app.exceptions.NotFoundException import NotFoundException
from app.repositories.aluno_repository import AlunoRepository
from app.schemas.aluno import AlunoCreate, AlunoUpdate


class AlunoService:
    def __init__(self, repository: AlunoRepository):
        self.repository = repository
        
    def create(self, data: AlunoCreate):
        matricula_existe = self.repository.get_aluno_by_matricula(data.matricula)
        if matricula_existe:
            raise DuplicateFieldException("Um aluno com essa matricula já existe!")
        return self.repository.create(data)
    
    def list_alunos(self):
        return self.repository.list_alunos()
    
    def get_aluno_by_id(self, id: UUID):
        aluno = self.repository.get_aluno_by_id(id)
        if not aluno:
            raise NotFoundException("Aluno com esse ID não foi encontrado")
        return aluno
    
    def delete_aluno_by_id(self, id: UUID):
        aluno = self.repository.get_aluno_by_id(id)
        if not aluno:
            raise NotFoundException("Aluno com esse ID não foi encontrado")
        self.repository.delete_aluno(aluno)
        
    def get_aluno_by_matricula(self, matricula: str):
        aluno = self.repository.get_aluno_by_matricula(matricula)
        if not aluno:
            raise NotFoundException("Aluno com essa matricula não foi encontrado")
        return aluno
    
    def update_turma_aluno(self, data_atualizar: AlunoUpdate):
        aluno = self.repository.insert_aluno_turma(data_atualizar)
        if not aluno:
            raise NotFoundException("Aluno não foi encontrado")
        return aluno
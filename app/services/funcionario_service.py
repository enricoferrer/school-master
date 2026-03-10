from uuid import UUID

from app.repositories.funcionario_repository import FuncionarioRepository
from app.schemas.funcionarios import FuncionarioCreate
from app.exceptions import NotFoundException

class FuncionarioService:
    def __init__(self, repository: FuncionarioRepository):
        self.repository = repository
        
    def create(self, data: FuncionarioCreate):
        return self.repository.create(data)
    
    def get_funcionario_by_id(self, id: UUID):
        funcionario = self.repository.get_funcionario_by_id(id)
        
        if funcionario is None:
            raise NotFoundException(f"Funcionario com o ID: `{id}` não foi encontrado!")
        
        return funcionario
    
    def list_funcionario(self):
        return self.repository.list_all_funcionarios()
    
    def delete_funcionario(self, id: UUID):
        funcionario = self.get_funcionario_by_id(id)
        self.repository.delete_funcionario_by_id(funcionario)
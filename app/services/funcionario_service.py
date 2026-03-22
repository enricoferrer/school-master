from uuid import UUID

from app.repositories.funcionario_repository import FuncionarioRepository
from app.schemas.funcionarios import FuncionarioCreate
from app.exceptions import NotFoundException

class FuncionarioService:
    def __init__(self, repository: FuncionarioRepository):
        self.repository = repository
        
    async def create(self, data: FuncionarioCreate):
        return await self.repository.create(data)
    
    async def get_funcionario_by_id(self, id: UUID):
        funcionario = await self.repository.get_funcionario_by_id(id)
        
        if funcionario is None:
            raise NotFoundException(f"Funcionario com o ID: `{id}` não foi encontrado!")
        
        return funcionario
    
    async def list_funcionario(self):
        return await self.repository.list_all_funcionarios()
    
    async def delete_funcionario(self, id: UUID):
        funcionario = await self.get_funcionario_by_id(id)
        await self.repository.delete_funcionario(funcionario)
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.funcionario import Funcionario
from app.schemas.funcionarios import FuncionarioCreate

class FuncionarioRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        
    def _base_query(self):
        return select(Funcionario).options(
            selectinload(Funcionario.usuario)
        )
        
    async def create(self, data: FuncionarioCreate):
        funcionario = Funcionario(**data.model_dump())
        self.db.add(funcionario)
        await self.db.commit()
        await self.db.refresh(funcionario)
        result = await self.db.execute(
            self._base_query().where(Funcionario.id == funcionario.id)
        )
        
        funcionario = result.scalar_one_or_none()
        return funcionario
    
    async def list_all_funcionarios(self):
        result = await self.db.execute(self._base_query())
        return result.scalars().all()
    
    async def get_funcionario_by_id(self, id: UUID):
        result = await self.db.execute(self._base_query().where(Funcionario.id == id))
        return result.scalar_one_or_none()
    
    async def delete_funcionario(self, funcionario: Funcionario):
        await self.db.delete(funcionario)
        await self.db.commit()
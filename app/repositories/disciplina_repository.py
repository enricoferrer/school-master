from sqlalchemy import select
from uuid import UUID

from app.schemas.disciplina import DisciplinaCreate
from app.models.disciplina import Disciplina
from sqlalchemy.ext.asyncio import AsyncSession

class DisciplinaRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, data: DisciplinaCreate):
        disciplina = Disciplina(**data.model_dump())
        self.db.add(disciplina)
        await self.db.commit()
        await self.db.refresh(disciplina)
        return disciplina
    
    async def list_disciplina(self):
        result = await self.db.execute(select(Disciplina))
        return result.scalars().all()
    
    async def get_disciplina_by_id(self, id: UUID):
        result = await self.db.execute(select(Disciplina).where(Disciplina.id == id))
        return result.scalar_one_or_none()
    
    async def delete_disciplina(self, disciplina: Disciplina):
        await self.db.delete(disciplina)
        await self.db.commit()
        
    async def get_disciplina_by_codigo(self, codigo: str):
        result = await self.db.execute(select(Disciplina).where(Disciplina.codigo == codigo))
        return result.scalar_one_or_none()
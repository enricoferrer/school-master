from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.turma import Turma
from app.schemas.turma import TurmaCreate


class TurmaRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        
    async def create(self, data: TurmaCreate):
        turma = Turma(**data.model_dump())
        self.db.add(turma)
        await self.db.commit()
        await self.db.refresh(turma)
        return turma
    
    async def list_turmas(self):
        turmas = await self.db.execute(select(Turma))
        return turmas.scalars().all()
    
    async def get_turma_by_id(self, id: UUID):
        return await self.db.scalar(select(Turma).where(Turma.id == id))
    
    async def turma_existe(self, sala: str, serie: str) -> bool:
        turma = await self.db.scalar(select(Turma).where((Turma.sala == sala) & (Turma.serie == serie)))
        return bool(turma)
    
    async def delete_turma(self, turma: Turma):
        await self.db.delete(turma)
        await self.db.commit()
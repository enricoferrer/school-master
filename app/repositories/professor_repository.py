from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.schemas.professor import ProfessorCreate
from app.models.professor import Professor

class ProfessorRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        
    async def create(self, data: ProfessorCreate):
        professor = Professor(**data.model_dump())
        self.db.add(professor)
        await self.db.commit()
        await self.db.refresh(professor)
        return professor
    
    async def list_all_professor(self):
        result = await self.db.execute(select(Professor))
        return result.scalars().all()
    
    async def get_professor_by_id(self, id: UUID):
        result = await self.db.execute(
            select(Professor).where(Professor.id == id)
        )
        return result.scalar_one_or_none()
    
    async def delete_professor(self, professor: Professor):
        await self.db.delete(professor)
        await self.db.commit()
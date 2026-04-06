from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.schemas.aluno_responsavel import AlunoResponsavelCreate
from app.models.aluno_responsavel import AlunoResponsavel
from sqlalchemy import select

class AlunoResponsavelRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, data: AlunoResponsavelCreate) -> AlunoResponsavel:
        responsavel = AlunoResponsavel(**data.model_dump())
        self.db.add(responsavel)
        await self.db.commit()
        await self.db.refresh(responsavel)
        return responsavel
    
    async def delete(self, fk_aluno: UUID, fk_responsavel: UUID):
        result = self.search_responsavel_by_id(fk_aluno, fk_responsavel)
        responsavel = result.scalar_one_or_none()
        if responsavel:
            await self.db.delete(responsavel)
            await self.db.commit()
        
    async def search_responsavel_by_id(self, fk_aluno: UUID, fk_responsavel: UUID) -> AlunoResponsavel | None:
        result = await self.db.execute(
            select(AlunoResponsavel).where(
                AlunoResponsavel.fk_aluno == fk_aluno,
                AlunoResponsavel.fk_responsavel == fk_responsavel
            )
        )
        return result.scalar_one_or_none()
    
    async def list_responsaveis_by_aluno(self, fk_aluno: UUID) -> list[AlunoResponsavel]:
        result = await self.db.execute(
            select(AlunoResponsavel).where(AlunoResponsavel.fk_aluno == fk_aluno)
        )
        return result.scalars().all()
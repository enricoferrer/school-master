from sqlalchemy import UUID, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.aluno import Aluno
from app.schemas.aluno import AlunoCreate, AlunoUpdate


class AlunoRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        
    def _base_query(self):
        return select(Aluno).options(
            selectinload(Aluno.turma),
            selectinload(Aluno.usuario)
        )
        
    async def create(self, data: AlunoCreate):
        aluno = Aluno(**data.model_dump())
        self.db.add(aluno)
        await self.db.commit()
        await self.db.refresh(aluno)
        result = await self.db.execute(
            self._base_query().where(Aluno.id == aluno.id)
        )
        
        aluno = result.scalar_one()
        
        return aluno
    
    async def list_alunos(self):
        result = await self.db.execute(self._base_query())
        return result.scalars().all()
    
    async def get_aluno_by_id(self, id: UUID):
        result = await self.db.execute(
            self._base_query().where(Aluno.id == id)
        )
        return result.scalar_one_or_none()
    
    async def delete_aluno(self, aluno: Aluno):
        await self.db.delete(aluno)
        await self.db.commit()
        
    async def get_aluno_by_matricula(self, matricula: str):
        result = await self.db.execute(
            self._base_query().where(Aluno.matricula == matricula)
        )
        return result.scalar_one_or_none()
    
    async def insert_aluno_turma(self, data_atualizar: AlunoUpdate):
        aluno = await self.get_aluno_by_id(data_atualizar.id)

        if not aluno:
            return None

        aluno.fk_turma = data_atualizar.fk_turma

        await self.db.commit()
        await self.db.refresh(aluno)

        # 🔥 reload com relationships
        result = await self.db.execute(
            self._base_query().where(Aluno.id == aluno.id)
        )

        return result.scalar_one()
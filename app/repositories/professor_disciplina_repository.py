from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.schemas.professor_disciplina import ProfessorDisciplinaCreate
from app.models.professor_disciplina import ProfessorDisciplina

class ProfessorDisciplinaRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        
    def _base_query(self):
        return select(ProfessorDisciplina).options(
            selectinload(ProfessorDisciplina.disciplina),
            selectinload(ProfessorDisciplina.professor)
        )
        
    async def create(self, data: ProfessorDisciplinaCreate):
        professor_disciplina = ProfessorDisciplina(**data.model_dump())
        self.db.add(professor_disciplina)
        await self.db.commit()
        await self.db.refresh(professor_disciplina)
        
        result = await self.db.execute(self._base_query().where(ProfessorDisciplina.id == professor_disciplina.id))
        
        professor_disciplina = result.scalar_one()
        
        return professor_disciplina
        
    async def vinculo_existe(self, fk_disciplina: UUID, fk_professor: UUID) -> bool:
        result = await self.db.execute(self._base_query().where((ProfessorDisciplina.fk_disciplina == fk_disciplina) & (ProfessorDisciplina.fk_professor == fk_professor)))
        return bool(result.scalar_one_or_none())
    
    async def list_disciplinas_do_professor(self, fk_professor: UUID):
        result = await self.db.execute(self._base_query().where(ProfessorDisciplina.fk_professor == fk_professor))
        return result.scalars().all()
    
    async def list_professores_da_disciplina(self, fk_disciplina: UUID):
        result = await self.db.execute(self._base_query().where(ProfessorDisciplina.fk_disciplina == fk_disciplina))
        return result.scalars().all()
    
    async def get_vinculo(self, fk_disciplina: UUID, fk_professor: UUID):
        result = await self.db.execute(self._base_query().where((ProfessorDisciplina.fk_disciplina == fk_disciplina) & (ProfessorDisciplina.fk_professor == fk_professor)))
        return result.scalar_one_or_none()
    
    async def delete_vinculo(self, vinculo: ProfessorDisciplina):
        await self.db.delete(vinculo)
        await self.db.commit()
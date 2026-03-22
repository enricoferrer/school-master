from sqlalchemy import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.turma_professores import TurmaProfessores
from app.schemas.turma_professores import TurmaProfessoresCreate


class TurmaProfessoresRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        
    def _base_query(self):
        return select(TurmaProfessores).options(
            selectinload(TurmaProfessores.disciplina),
            selectinload(TurmaProfessores.professor),
            selectinload(TurmaProfessores.turma)
        )
        
    async def create(self, data: TurmaProfessoresCreate):
        vinculo = TurmaProfessores(**data.model_dump())
        self.db.add(vinculo)
        await self.db.commit()
        await self.db.refresh(vinculo)
        
        result = await self.db.execute(self._base_query().where(TurmaProfessores.id == vinculo.id))
        
        vinculo = result.scalar_one()
        
        return vinculo
    
    async def get_vinculo_by_id(self, id: UUID):
        result = await self.db.execute(self._base_query().where(TurmaProfessores.id == id))
        return result.scalar_one_or_none()
    
    async def get_vinculo(self, id_turma: UUID, id_professor: UUID, id_disciplina):
        result = await self.db.execute(self._base_query().where((TurmaProfessores.fk_turma == id_turma) & (TurmaProfessores.fk_disciplina == id_disciplina) & (TurmaProfessores.fk_professor == id_professor)))
        return result.scalar_one_or_none()
    
    async def delete_vinculo(self, vinculo: TurmaProfessores):
        await self.db.delete(vinculo)
        await self.db.commit()
        
    async def list_turmas_do_professor(self, id_professor: UUID):
        result = await self.db.execute(self._base_query().where(TurmaProfessores.fk_professor == id_professor))
        return result.scalars().all()
    
    async def list_professores_da_turma(self, id_turma: UUID):
        result = await self.db.execute(self._base_query().where(TurmaProfessores.fk_turma == id_turma))
        return result.scalars().all()
    
    async def vinculo_ja_existe(self, id_turma: UUID, id_professor: UUID, id_disciplina) -> bool:
        result = await self.db.execute(self._base_query().where((TurmaProfessores.fk_turma == id_turma) & (TurmaProfessores.fk_disciplina == id_disciplina) & (TurmaProfessores.fk_professor == id_professor)))
        return bool(result.scalar_one_or_none())
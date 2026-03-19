from sqlalchemy import UUID
from sqlalchemy.orm import Session

from app.models.turma_professores import TurmaProfessores
from app.schemas.turma_professores import TurmaProfessoresCreate


class TurmaProfessoresRepository:
    def __init__(self, db: Session):
        self.db = db
        
    def create(self, data: TurmaProfessoresCreate):
        vinculo = TurmaProfessores(**data.model_dump())
        self.db.add(vinculo)
        self.db.commit()
        self.db.refresh(vinculo)
        return vinculo
    
    def get_vinculo_by_id(self, id: UUID):
        vinculo = self.db.query(TurmaProfessores).filter(TurmaProfessores.id == id).first()
        return vinculo
    
    def delete_vinculo(self, vinculo: TurmaProfessores):
        self.db.delete(vinculo)
        self.db.commit()
        
    def list_turmas_do_professor(self, id_professor: UUID):
        turmas = self.db.query(TurmaProfessores).filter(TurmaProfessores.fk_professor == id_professor).all()
        return turmas
    
    def list_professores_da_turma(self, id_turma: UUID):
        professores = self.db.query(TurmaProfessores).filter(TurmaProfessores.fk_turma == id_turma).all()
        return professores
    
    def vinculo_ja_existe(self, id_turma: UUID, id_professor: UUID, id_disciplina) -> bool:
        vinculo_existe = self.db.query(TurmaProfessores).filter((TurmaProfessores.fk_turma == id_turma) & (TurmaProfessores.fk_disciplina == id_disciplina) & (TurmaProfessores.fk_professor == id_professor)).first()
        return bool(vinculo_existe)
from sqlalchemy import UUID
from sqlalchemy.orm import Session

from app.models.aluno import Aluno
from app.schemas.aluno import AlunoResponse


class AlunoRepository:
    def __init__(self, db: Session):
        self.db = db
        
    def create(self, data: AlunoResponse):
        aluno = Aluno(**data.model_dump())
        self.db.add(aluno)
        self.db.commit()
        self.db.refresh(aluno)
        return aluno
    
    def list_alunos(self):
        return self.db.query(Aluno).all()
    
    def get_aluno_by_id(self, id: UUID):
        return self.db.query(Aluno).filter(Aluno.id == id).first()
    
    def delete_aluno(self, aluno: Aluno):
        self.db.delete(aluno)
        self.db.commit()
        
    def get_aluno_by_matricula(self, matricula: str):
        return self.db.query(Aluno).filter(Aluno.matricula == matricula).first()
from uuid import UUID

from sqlalchemy.orm import Session
from app.models.funcionario import Funcionario
from app.schemas.funcionarios import FuncionarioCreate

class FuncionarioRepository:
    def __init__(self, db: Session):
        self.db = db
        
    def create(self, data: FuncionarioCreate):
        funcionario = Funcionario(**data.model_dump())
        self.db.add(funcionario)
        self.db.commit()
        self.db.refresh(funcionario)
        return funcionario
    
    def list_all_funcionarios(self):
        return self.db.query(Funcionario).all()
    
    def get_funcionario_by_id(self, id: UUID):
        return self.db.query(Funcionario).filter(Funcionario.id == id).first()
    
    def delete_funcionario_by_id(self, id: UUID):
        funcionario = self.get_funcionario_by_id(id)
        self.db.delete(funcionario)
        self.db.commit()
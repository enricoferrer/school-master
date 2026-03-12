from uuid import UUID

from sqlalchemy.orm import Session
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCreate

class UsuarioRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: UsuarioCreate):
        usuario = Usuario(**data.model_dump())
        self.db.add(usuario)
        self.db.commit()
        self.db.refresh(usuario)
        return usuario
    
    def list_usuarios(self):
        return self.db.query(Usuario).all()

    def get_usuario_by_id(self, id: UUID):
        return self.db.query(Usuario).filter(Usuario.id == id).first()
    
    def delete_usuario(self, usuario: Usuario):
        self.db.delete(usuario)
        self.db.commit()
        
    def get_usuario_by_cpf(self, cpf: str):
        return self.db.query(Usuario).filter(Usuario.cpf == cpf).first()
    
    def get_usuario_by_rg(self, rg: str):
        return self.db.query(Usuario).filter(Usuario.registro_geral == rg).first()
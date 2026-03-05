from sqlalchemy.orm import Session
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCreate

class UsuarioRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: UsuarioCreate):
        usuario = Usuario(**data.model_dump)
        self.db.add(usuario)
        self.db.commit()
        self.db.refresh(usuario)
        return usuario
    
    def list_usuarios(self):
        return self.db.query(Usuario).all()

    def get_usuario_by_id(self, id: str):
        return self.db.query(Usuario).filter(Usuario.id == id).first()
    
    def delete_usuario_by_id(self, id: str):
        usuario = self.get_usuario_by_id(id)
        self.db.delete(usuario)
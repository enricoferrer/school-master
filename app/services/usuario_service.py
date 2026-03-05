from app.repositories.usuario_repository import UsuarioRepository
from app.schemas.usuario import UsuarioCreate

class UsuarioService():
    def __init__(self, repository: UsuarioRepository):
        self.repository = repository
        
    def create(self, data: UsuarioCreate):
        return self.repository.create(data)
    
    def list_usuarios(self):
        return self.repository.list_usuarios()
    
    def get_usuario_by_id(self, id: str):
        return self.repository.get_usuario_by_id(id)
    
    def delete_usuario_by_id(self, id: str):
        self.repository.delete_usuario_by_id(id)
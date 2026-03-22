from app.core.security import hash_password
from app.repositories.usuario_repository import UsuarioRepository
from app.schemas.usuario import UsuarioCreate
from app.exceptions.NotFoundException import NotFoundException
from uuid import UUID
from app.exceptions.DuplicateFieldException import DuplicateFieldException

class UsuarioService():
    def __init__(self, repository: UsuarioRepository):
        self.repository = repository
        
    async def create(self, data: UsuarioCreate):
        usuarioDuplicadoCpf = await self.repository.get_usuario_by_cpf(data.cpf)
        usuarioDuplicadoRg = await self.repository.get_usuario_by_rg(data.registro_geral)
        
        if usuarioDuplicadoCpf:
            raise DuplicateFieldException(f"Usuário com esse CPF já existe!")
        
        if usuarioDuplicadoRg:
            raise DuplicateFieldException(f"Usuário com esse RG já existe!")
        
        senha_criptada = hash_password(data.senha_hash)
        data.senha_hash = senha_criptada

        return await self.repository.create(data)
    
    async def list_usuarios(self):
        return await self.repository.list_usuarios()
    
    async def get_usuario_by_id(self, id: UUID):
        usuario = await self.repository.get_usuario_by_id(id)
        if usuario is None:
            raise NotFoundException(f"Usuario com o ID: '{id} não foi encontrado!")
        return usuario
    
    async def delete_usuario_by_id(self, id: UUID):
        usuario = await self.get_usuario_by_id(id)
        await self.repository.delete_usuario(usuario)
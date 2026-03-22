from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCreate

class UsuarioRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: UsuarioCreate):
        usuario = Usuario(**data.model_dump())
        self.db.add(usuario)
        await self.db.commit()
        await self.db.refresh(usuario)
        return usuario
    
    async def list_usuarios(self):
        result = await self.db.execute(select(Usuario))
        return result.scalars().all()

    async def get_usuario_by_id(self, id: UUID):
        result = await self.db.execute(
            select(Usuario).where(Usuario.id == id)
        )
        return result.scalar_one_or_none()

    async def delete_usuario(self, usuario: Usuario):
        await self.db.delete(usuario)
        await self.db.commit()
        
    async def get_usuario_by_cpf(self, cpf: str):
        return await self.db.scalar(select(Usuario).where(Usuario.cpf == cpf))
    
    async def get_usuario_by_rg(self, rg: str):
        return await self.db.scalar(select(Usuario).where(Usuario.registro_geral == rg))
    
    async def get_usuario_by_email(self, email: str):
        result = await self.db.execute(
            select(Usuario).where(Usuario.email == email)
        )
        return result.scalar_one_or_none()
    
    async def atualizar_usuario(self, usuario: Usuario):
        self.db.add(usuario)
        await self.db.commit()
        await self.db.refresh(usuario)
        return usuario
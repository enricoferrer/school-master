from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.role import Role


class RoleRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        
    async def get_role_by_id(self, role_id: int) -> Role | None:
        return await self.db.scalar(     
            select(Role).where(Role.id == role_id)
        )
from typing import Set

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.role import Role
from app.models.role_permissions import RolePermission

class RolePermissionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        
    async def get_permissions_by_role_name(self, role_name: str) -> Set[str]:
        result = await self.db.execute(
            select(RolePermission.permission)
            .join(Role, Role.id == RolePermission.fk_role)
            .where(Role.nome == role_name.upper())
        )
        return {row[0] for row in result.all()}
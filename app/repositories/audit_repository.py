from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog


class AuditRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        
    async def registrar_log(self, log: AuditLog):
        self.db.add(log)
        await self.db.commit()
# repositories/audit_log_repository.py
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog
from app.schemas.audit_log import AuditLogFilters


class AuditLogRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def registrar_log(self, log: AuditLog) -> None:
        self.db.add(log)
        await self.db.commit()

    async def listar(self, filters: AuditLogFilters) -> tuple[list[AuditLog], int]:
        query = select(AuditLog)

        if filters.user_id:
            query = query.where(AuditLog.fk_usuario == filters.user_id)

        if filters.data_de:
            query = query.where(AuditLog.timestamp >= filters.data_de)

        if filters.data_ate:
            query = query.where(AuditLog.timestamp <= filters.data_ate)

        if filters.entidade:
            query = query.where(AuditLog.tabela_afetada == filters.entidade)

        if filters.operacao:
            query = query.where(AuditLog.operacao == filters.operacao.upper())

        count_result = await self.db.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = count_result.scalar_one()

        offset = (filters.page - 1) * filters.page_size
        query  = query.order_by(AuditLog.timestamp.desc())
        query  = query.offset(offset).limit(filters.page_size)

        result = await self.db.execute(query)
        items  = result.scalars().all()

        return items, total
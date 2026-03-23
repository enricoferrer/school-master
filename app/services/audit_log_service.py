from datetime import datetime
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog
from app.repositories.audit_log_repository import AuditLogRepository
from app.schemas.audit_log import AuditLogFilters


class AuditLogService:
    def __init__(self, repo: AuditLogRepository):
        self.repo = repo

    async def list(self, filters: AuditLogFilters) -> dict:
        items, total = await self.repo.listar(filters)

        return {
            "total":     total,
            "page":      filters.page,
            "page_size": filters.page_size,
            "items":     items,
        }
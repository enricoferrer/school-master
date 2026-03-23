from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from uuid import UUID
from datetime import datetime

from app.core.database import get_db
from app.dependencies.auth import require_permission, CurrentUser
from app.repositories.audit_log_repository import AuditLogRepository
from app.schemas.audit_log import AuditLogResponse, AuditLogFilters
from app.services.audit_log_service import AuditLogService

router = APIRouter(prefix="/audit-logs", tags=["Auditoria"])

def get_audit_log_service(db: AsyncSession = Depends(get_db)) -> AuditLogService:
    return AuditLogService(AuditLogRepository(db))

@router.get("", response_model=dict, status_code=200)
async def list_audit_logs(
    current_user: Annotated[None, Depends(require_permission("audit:read"))],
    service:      AuditLogService = Depends(get_audit_log_service),
    user_id:      UUID     | None = Query(None),
    data_de:      datetime | None = Query(None),
    data_ate:     datetime | None = Query(None),
    entidade:     str      | None = Query(None),
    operacao:     str      | None = Query(None),
    page:         int             = Query(1, ge=1),
    page_size:    int             = Query(50, ge=1, le=200),
):
    filters = AuditLogFilters(
        user_id=user_id, data_de=data_de, data_ate=data_ate,
        entidade=entidade, operacao=operacao,
        page=page, page_size=page_size,
    )
    result = await service.list(filters)

    return {
        "total":     result["total"],
        "page":      result["page"],
        "page_size": result["page_size"],
        "items":     [AuditLogResponse.model_validate(i) for i in result["items"]],
    }
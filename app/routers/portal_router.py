# routers/portal_router.py
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database                       import get_db
from app.dependencies.auth                   import require_permission, TokenData
from app.repositories.notificacao_repository import NotificacaoRepository
from app.schemas.portal                      import PortalAlunoResponse
from app.services.notificacao_service        import NotificacaoService

router = APIRouter(prefix="/portal", tags=["Portal do Responsável"])


def get_notificacao_service(db: AsyncSession = Depends(get_db)) -> NotificacaoService:
    return NotificacaoService(NotificacaoRepository(db))


@router.get("/aluno/{aluno_id}", response_model=PortalAlunoResponse, responses={
    403: {"description": "Você não tem vínculo com este aluno"},
})
async def portal_aluno(
    aluno_id:     UUID,
    current_user: Annotated[TokenData, Depends(require_permission("portal:read"))],
    service:      NotificacaoService = Depends(get_notificacao_service),
):
    try:
        return await service.portal_aluno(
            responsavel_id = UUID(current_user.user_id),
            aluno_id       = aluno_id,
        )
    except HTTPException:
        raise
# routers/notificacao_router.py
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database                       import get_db
from app.dependencies.auth                   import require_permission, TokenData
from app.repositories.notificacao_repository import NotificacaoRepository
from app.schemas.notificacao                 import (
    NotificacaoResponse, PreferenciaCreate, PreferenciaResponse,
)
from app.services.notificacao_service import NotificacaoService

router = APIRouter(prefix="/notificacoes", tags=["Notificações"])


def get_notificacao_service(db: AsyncSession = Depends(get_db)) -> NotificacaoService:
    return NotificacaoService(NotificacaoRepository(db))


@router.get("", response_model=list[NotificacaoResponse])
async def listar_notificacoes(
    current_user: Annotated[TokenData, Depends(require_permission("notificacao:read"))],
    service:      NotificacaoService = Depends(get_notificacao_service),
):
    notifs = await service.repo.listar_por_usuario(UUID(current_user.user_id))
    return [NotificacaoResponse.model_validate(n) for n in notifs]


@router.post("/{notificacao_id}/reenviar", responses={
    404: {"description": "Notificação não encontrada"},
    409: {"description": "Notificação já foi enviada com sucesso"},
})
async def reenviar_notificacao(
    notificacao_id: UUID,
    current_user:   Annotated[TokenData, Depends(require_permission("notificacao:write"))],
    service:        NotificacaoService = Depends(get_notificacao_service),
):
    try:
        return await service.reenviar(notificacao_id)
    except HTTPException:
        raise


@router.put("/preferencias", response_model=PreferenciaResponse)
async def salvar_preferencia(
    body:         PreferenciaCreate,
    current_user: Annotated[TokenData, Depends(require_permission("notificacao:read"))],
    service:      NotificacaoService = Depends(get_notificacao_service),
):
    return await service.salvar_preferencia(UUID(current_user.user_id), body)


@router.get("/preferencias", response_model=list[PreferenciaResponse])
async def listar_preferencias(
    current_user: Annotated[TokenData, Depends(require_permission("notificacao:read"))],
    service:      NotificacaoService = Depends(get_notificacao_service),
):
    return await service.listar_preferencias(UUID(current_user.user_id))
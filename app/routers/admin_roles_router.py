import logging
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.dependencies.auth import require_permission
from app.models.role import Role
from app.models.audit_log import AuditLog
from app.schemas.rbac import RoleAssignRequest, RoleAssignResponse, RoleRevokeResponse
from app.services.rbac_service import invalidate_role_cache

router = APIRouter(prefix="/admin/roles", tags=["Admin — Controle de Acesso"])

@router.patch(
    "/assign",
    response_model=RoleAssignResponse,
    summary="Atribuir papel a usuário",
    status_code=status.HTTP_200_OK,
)
async def assign_role(
    body: RoleAssignRequest,
    request: Request,
    current_user = Depends(require_permission("role:assign")),
    db: AsyncSession = Depends(get_db),
):
    """
    Atribui um novo papel a um usuário.
    Requer permissão `role:assign` (exclusiva de ADMIN).
    Invalida o cache Redis do papel alterado e registra no audit_log.
    """
    from app.models.usuario import Usuario  # ajuste o import

    # Busca usuário alvo
    usuario = await db.scalar(select(Usuario).where(Usuario.id == body.usuario_id))
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    # Busca papel atual (para audit log)
    role_anterior = await db.scalar(
        select(Role.nome).where(Role.id == usuario.fk_role)
    )

    # Busca novo papel
    novo_role = await db.scalar(select(Role).where(Role.nome == body.role_nome))
    if not novo_role:
        raise HTTPException(status_code=400, detail=f"Papel '{body.role_nome}' não existe no banco")

    if role_anterior == novo_role.nome:
        raise HTTPException(status_code=409, detail="Usuário já possui este papel")

    # Atualiza FK do usuário
    usuario.fk_role = novo_role.id

    # Audit log
    db.add(AuditLog(
        fk_usuario        = UUID(current_user.user_id),
        operacao          = "ROLE_ASSIGN",
        tabela_afetada    = "usuarios",
        registro_id       = usuario.id,
        dados_anteriores  = {"role": role_anterior},
        dados_posteriores = {
            "role"         : novo_role.nome,
            "usuario_alvo" : str(body.usuario_id),
            "admin"        : current_user.user_id,
            "timestamp"    : datetime.now(timezone.utc).isoformat(),
        },
        ip_origem         = request.client.host if request.client else "unknown",
        user_agent        = request.headers.get("user-agent", ""),
    ))

    await db.commit()

    # Invalida cache do papel anterior e do novo para evitar state stale
    if role_anterior:
        await invalidate_role_cache(role_anterior)
    await invalidate_role_cache(novo_role.nome)

    return RoleAssignResponse(
        message       = f"Papel '{novo_role.nome}' atribuído com sucesso.",
        usuario_id    = body.usuario_id,
        role_anterior = role_anterior,
        role_novo     = novo_role.nome,
    )


@router.patch(
    "/revoke",
    response_model=RoleRevokeResponse,
    summary="Revogar papel (retorna para ALUNO)",
    status_code=status.HTTP_200_OK,
)
async def revoke_role(
    body: RoleAssignRequest,
    request: Request,
    current_user = Depends(require_permission("role:revoke")),
    db: AsyncSession = Depends(get_db),
):
    """
    Revoga o papel atual e retorna o usuário ao papel base ALUNO.
    Requer permissão `role:revoke` (exclusiva de ADMIN).
    """
    from app.models.usuario import Usuario

    usuario = await db.scalar(select(Usuario).where(Usuario.id == body.usuario_id))
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    role_anterior = await db.scalar(
        select(Role.nome).where(Role.id == usuario.fk_role)
    )

    if role_anterior == "ALUNO":
        raise HTTPException(status_code=409, detail="Usuário já está no papel base ALUNO")

    role_base = await db.scalar(select(Role).where(Role.nome == "ALUNO"))
    if not role_base:
        raise HTTPException(status_code=500, detail="Papel base ALUNO não encontrado no banco")

    usuario.fk_role = role_base.id

    db.add(AuditLog(
        fk_usuario        = UUID(current_user.user_id),
        operacao          = "ROLE_REVOKE",
        tabela_afetada    = "usuarios",
        registro_id       = usuario.id,
        dados_anteriores  = {"role": role_anterior},
        dados_posteriores = {
            "role"         : "ALUNO",
            "usuario_alvo" : str(body.usuario_id),
            "admin"        : current_user.user_id,
            "timestamp"    : datetime.now(timezone.utc).isoformat(),
        },
        ip_origem         = request.client.host if request.client else "unknown",
        user_agent        = request.headers.get("user-agent", ""),
    ))

    await db.commit()
    await invalidate_role_cache(role_anterior or "ADMIN")

    return RoleRevokeResponse(
        message       = "Papel revogado. Usuário retornou ao papel base ALUNO.",
        usuario_id    = body.usuario_id,
        role_anterior = role_anterior,
    )
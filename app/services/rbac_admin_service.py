import logging
from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status

from app.repositories.usuario_repository import UsuarioRepository
from app.repositories.role_repository import RoleRepository
from app.repositories.audit_log_repository import AuditLogRepository
from app.models.audit_log import AuditLog
from app.schemas.rbac import RoleAssignRequest, RoleAssignResponse, RoleRevokeResponse
from app.services.rbac_service import invalidate_role_cache
from app.exceptions.EntityNotFoundException import EntityNotFoundException
from app.exceptions.NotFoundException import NotFoundException
from app.exceptions.DuplicateFieldException import DuplicateFieldException

logger = logging.getLogger(__name__)

ROLE_BASE = "ALUNO"


class RbacAdminService:
    def __init__(
        self,
        usuario_repo: UsuarioRepository,
        role_repo:    RoleRepository,
        audit_repo:   AuditLogRepository,
    ) -> None:
        self.usuario_repo = usuario_repo
        self.role_repo    = role_repo
        self.audit_repo   = audit_repo

    # ── assign ────────────────────────────────────────────────

    async def assign_role(
        self,
        body:       RoleAssignRequest,
        admin_id:   str,
        ip:         str,
        user_agent: str,
    ) -> RoleAssignResponse:

        usuario = await self.usuario_repo.get_usuario_by_id(body.usuario_id)
        if not usuario:
            raise EntityNotFoundException("Usuário não encontrado")

        role_anterior = await self.role_repo.get_role_by_id(usuario.fk_role)
        nome_anterior = role_anterior.nome if role_anterior else None

        novo_role = await self.role_repo.get_role_by_name(body.role_nome)
        if not novo_role:
            raise NotFoundException(f"Papel '{body.role_nome}' não existe no banco")

        if nome_anterior == novo_role.nome:
            raise DuplicateFieldException("Usuário já possui este papel")

        usuario.fk_role = novo_role.id
        await self.usuario_repo.atualizar_usuario(usuario)

        await self.audit_repo.registrar_log(AuditLog(
            fk_usuario        = UUID(admin_id),
            operacao          = "ROLE_ASSIGN",
            tabela_afetada    = "usuarios",
            registro_id       = usuario.id,
            dados_anteriores  = {"role": nome_anterior},
            dados_posteriores = {
                "role"         : novo_role.nome,
                "usuario_alvo" : str(body.usuario_id),
                "admin"        : admin_id,
                "timestamp"    : datetime.now(timezone.utc).isoformat(),
            },
            ip_origem         = ip,
            user_agent        = user_agent,
        ))

        if nome_anterior:
            await invalidate_role_cache(nome_anterior)
        await invalidate_role_cache(novo_role.nome)

        logger.info("ROLE_ASSIGN | admin=%s | target=%s | %s → %s",
                    admin_id, body.usuario_id, nome_anterior, novo_role.nome)

        return RoleAssignResponse(
            message       = f"Papel '{novo_role.nome}' atribuído com sucesso.",
            usuario_id    = body.usuario_id,
            role_anterior = nome_anterior,
            role_novo     = novo_role.nome,
        )

    # ── revoke ────────────────────────────────────────────────

    async def revoke_role(
        self,
        body:       RoleAssignRequest,
        admin_id:   str,
        ip:         str,
        user_agent: str,
    ) -> RoleRevokeResponse:

        usuario = await self.usuario_repo.get_usuario_by_id(body.usuario_id)
        if not usuario:
            raise EntityNotFoundException("Usuário não encontrado")

        role_atual = await self.role_repo.get_role_by_id(usuario.fk_role)
        nome_atual = role_atual.nome if role_atual else None

        if nome_atual == ROLE_BASE:
            raise DuplicateFieldException("Usuário já está no papel base ALUNO")

        role_base = await self.role_repo.get_role_by_name(ROLE_BASE)
        if not role_base:
            raise NotFoundException("Papel base ALUNO não encontrado no banco")

        usuario.fk_role = role_base.id
        await self.usuario_repo.atualizar_usuario(usuario)

        await self.audit_repo.registrar_log(AuditLog(
            fk_usuario        = UUID(admin_id),
            operacao          = "ROLE_REVOKE",
            tabela_afetada    = "usuarios",
            registro_id       = usuario.id,
            dados_anteriores  = {"role": nome_atual},
            dados_posteriores = {
                "role"         : ROLE_BASE,
                "usuario_alvo" : str(body.usuario_id),
                "admin"        : admin_id,
                "timestamp"    : datetime.now(timezone.utc).isoformat(),
            },
            ip_origem         = ip,
            user_agent        = user_agent,
        ))

        if nome_atual:
            await invalidate_role_cache(nome_atual)

        logger.info("ROLE_REVOKE | admin=%s | target=%s | %s → %s",
                    admin_id, body.usuario_id, nome_atual, ROLE_BASE)

        return RoleRevokeResponse(
            message       = "Papel revogado. Usuário retornou ao papel base ALUNO.",
            usuario_id    = body.usuario_id,
            role_anterior = nome_atual,
        )
import logging
from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_token
from app.core.database import get_db          # ajuste o import conforme seu projeto
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.role_permission_repository import RolePermissionRepository
from app.services.rbac_service import get_permissions_for_role

logger = logging.getLogger(__name__)
_bearer = HTTPBearer(auto_error=True)


class TokenData:
    """Dados extraídos do JWT. Não acessa banco."""

    __slots__ = ("user_id", "role")

    def __init__(self, user_id: str, role: str) -> None:
        self.user_id = user_id
        self.role    = role
        
# ── Factories de repositórios ─────────────────────────────────────────────────

def get_role_permission_repo(db: AsyncSession = Depends(get_db)) -> RolePermissionRepository:
    return RolePermissionRepository(db)

def get_audit_repo(db: AsyncSession = Depends(get_db)) -> AuditLogRepository:
    return AuditLogRepository(db)

# ── Dependência 1: autenticação ──────────────────────────────────────────────

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> TokenData:
    """
    Valida o JWT e extrai user_id + role.
    Não acessa banco nem Redis — só decodifica o token.
    """
    try:
        payload = decode_token(credentials.credentials)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id: str | None = payload.get("sub")
    role: str | None    = payload.get("role")

    if not user_id or not role:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token malformado: 'sub' ou 'role' ausente",
        )

    return TokenData(user_id=user_id, role=role)


# ── Dependência 2: autorização (RBAC) ────────────────────────────────────────

def require_permission(permission: str):
    """
    Dependency factory — protege um endpoint por permissão.

    Exemplos de uso:
        # Como dependency simples (não precisa do user no handler):
        @router.get("/notas", dependencies=[Depends(require_permission("grade:read"))])

        # Quando precisa do usuário atual no handler:
        async def listar_notas(user: Annotated[TokenData, Depends(require_permission("grade:read"))]):
            ...
    """
    async def _guard(
        request: Request,
        current_user: TokenData = Depends(get_current_user),
        perm_repo:         RolePermissionRepository = Depends(get_role_permission_repo),
        audit_repo:        AuditLogRepository          = Depends(get_audit_repo),
    ) -> TokenData:

        permissions = await get_permissions_for_role(current_user.role, perm_repo)

        if permission not in permissions:
            # ── Grava audit_log ANTES de retornar 403 ────────────────
            await _write_access_denied_log(
                audit_repo     = audit_repo,
                user_id        = current_user.user_id,
                role           = current_user.role,
                permission_req = permission,
                endpoint       = request.url.path,
                method         = request.method,
                ip             = request.client.host if request.client else "unknown",
                user_agent     = request.headers.get("user-agent", ""),
            )

            logger.warning(
                "ACCESS_DENIED | user=%s | role=%s | permission=%s | %s %s",
                current_user.user_id, current_user.role,
                permission, request.method, request.url.path,
            )

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acesso negado. Permissão necessária: '{permission}'",
            )

        return current_user

    return _guard


# ── Helper interno ────────────────────────────────────────────────────────────

async def _write_access_denied_log(
    audit_repo: AuditLogRepository,
    user_id: str,
    role: str,
    permission_req: str,
    endpoint: str,
    method: str,
    ip: str,
    user_agent: str,
) -> None:
    """Grava ACCESS_DENIED no audit_log. Falha silenciosa para não mascarar o 403."""
    try:
        from app.models.audit_log import AuditLog  # import local para evitar circular

        await audit_repo.registrar_log(AuditLog(
            fk_usuario        = UUID(user_id),
            operacao          = "ACCESS_DENIED",
            tabela_afetada    = "endpoint",
            dados_posteriores = {
                "role"               : role,
                "permission_required": permission_req,
                "endpoint"           : endpoint,
                "method"             : method,
                "timestamp"          : datetime.now(timezone.utc).isoformat(),
            },
            ip_origem         = ip,
            user_agent        = user_agent,
        ))
    except Exception as exc:
        logger.error("Falha ao gravar audit_log de ACCESS_DENIED: %s", exc)


# ── Alias tipado para uso nos handlers ────────────────────────────────────────
# Uso: async def endpoint(user: CurrentUser): ...
CurrentUser = Annotated[TokenData, Depends(get_current_user)]
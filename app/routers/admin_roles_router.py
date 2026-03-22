from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import require_permission
from app.repositories.usuario_repository import UsuarioRepository
from app.repositories.role_repository import RoleRepository
from app.repositories.audit_repository import AuditRepository
from app.schemas.rbac import RoleAssignRequest, RoleAssignResponse, RoleRevokeResponse
from app.services.rbac_admin_service import RbacAdminService
from app.exceptions.EntityNotFoundException import EntityNotFoundException
from app.exceptions.NotFoundException import NotFoundException
from app.exceptions.DuplicateFieldException import DuplicateFieldException

router = APIRouter(prefix="/admin/roles", tags=["Admin — Controle de Acesso"])

def get_rbac_admin_service(db: AsyncSession = Depends(get_db)) -> RbacAdminService:
    return RbacAdminService(
        usuario_repo = UsuarioRepository(db),
        role_repo    = RoleRepository(db),
        audit_repo   = AuditRepository(db),
    )


@router.patch(
    "/assign",
    response_model=RoleAssignResponse,
    summary="Atribuir papel a usuário",
    status_code=status.HTTP_200_OK,
)
async def assign_role(
    body:         RoleAssignRequest,
    request:      Request,
    current_user  = Depends(require_permission("role:assign")),
    service:      RbacAdminService = Depends(get_rbac_admin_service),
):
    try:
        return await service.assign_role(
        body       = body,
        admin_id   = current_user.user_id,
        ip         = request.client.host if request.client else "unknown",
        user_agent = request.headers.get("user-agent", ""),
    )
    except EntityNotFoundException as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e))
    except NotFoundException as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))
    except DuplicateFieldException as e:
        raise HTTPException(status.HTTP_409_CONFLICT, str(e))


@router.patch(
    "/revoke",
    response_model=RoleRevokeResponse,
    summary="Revogar papel (retorna para ALUNO)",
    status_code=status.HTTP_200_OK,
)
async def revoke_role(
    body:         RoleAssignRequest,
    request:      Request,
    current_user  = Depends(require_permission("role:revoke")),
    service:      RbacAdminService = Depends(get_rbac_admin_service),
):
    try:
        return await service.revoke_role(
        body       = body,
        admin_id   = current_user.user_id,
        ip         = request.client.host if request.client else "unknown",
        user_agent = request.headers.get("user-agent", ""),
    )
    except EntityNotFoundException as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e))
    except NotFoundException as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))
    except DuplicateFieldException as e:
        raise HTTPException(status.HTTP_409_CONFLICT, str(e))
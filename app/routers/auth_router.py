from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.exceptions.EntityNotFoundException import EntityNotFoundException
from app.exceptions.WrongPasswordException import WrongPasswordException
from app.exceptions.BlockedAccountException import BlockedAccountException
from app.exceptions.InvalidTokenException import InvalidTokenException
from app.exceptions.InactiveUserException import InactiveUserException
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.role_repository import RoleRepository
from app.repositories.usuario_repository import UsuarioRepository
from app.schemas.auth import LoginRequest, TokenResponse, RefreshRequest
from app.services.auth_service import AuthService
from app.core.database import get_db

router = APIRouter(prefix="/auth", tags=["Autenticação"])

def get_service(db: AsyncSession = Depends(get_db)):
    audit_repository = AuditLogRepository(db)
    usuario_repository = UsuarioRepository(db)
    role_repository = RoleRepository(db)
    return AuthService(audit_repository, usuario_repository, role_repository)


@router.post("/login", response_model=TokenResponse, status_code=200)
async def login(payload: LoginRequest, request: Request, service: AuthService = Depends(get_service)):
    ip = request.client.host
    user_agent = request.headers.get("user-agent", "")
    try:
        tokens = await service.login(payload.email, payload.senha, ip, user_agent)
        return tokens
    except BlockedAccountException as e:
        raise HTTPException(status_code=401, detail=str(e))
    except WrongPasswordException as e:
        raise HTTPException(status_code=401, detail=str(e))
    except EntityNotFoundException as e:
        raise HTTPException(status_code=401, detail=str(e))

@router.post("/refresh", response_model=TokenResponse, status_code=200)
async def refresh(payload: RefreshRequest, service: AuthService = Depends(get_service)):
    try:
        return await service.refresh(payload.refresh_token)
    except InactiveUserException as e:
        raise HTTPException(status_code=403, detail=str(e))
    except InvalidTokenException as e:
        raise HTTPException(status_code=401, detail=str(e))
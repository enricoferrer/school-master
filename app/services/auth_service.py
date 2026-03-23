from datetime import datetime, timezone, timedelta
from http.client import HTTPException
from jose import JWTError

from sqlalchemy import select

from app.core.redis_client import get_redis
from app.exceptions.EntityNotFoundException import EntityNotFoundException
from app.exceptions.InactiveUserException import InactiveUserException
from app.models.role import Role
from app.models.usuario import Usuario
from app.models.audit_log import AuditLog
from app.exceptions.WrongPasswordException import WrongPasswordException
from app.exceptions.InvalidTokenException import InvalidTokenException
from app.exceptions.BlockedAccountException import BlockedAccountException
from app.repositories.audit_log_repository import AuditLogRepository
from app.core.security import verify_password, create_access_token, create_refresh_token, decode_token
from app.core.config import settings
from app.repositories.role_repository import RoleRepository
from app.repositories.usuario_repository import UsuarioRepository
from app.schemas.auth import TokenResponse

MAX_TENTATIVAS = 5
LOCKOUT_MINUTES = 15
REFRESH_TOKEN_PREFIX = "refresh:"


class AuthService:
    def __init__(
        self,
        audit_repository:   AuditLogRepository,
        usuario_repository: UsuarioRepository,
        role_repository:    RoleRepository,
    ):
        self.audit_repository   = audit_repository
        self.usuario_repository = usuario_repository
        self.role_repository    = role_repository

    # ── Público ───────────────────────────────────────────────────────────────

    async def login(self, email: str, senha: str, ip: str, user_agent: str) -> TokenResponse:
        usuario = await self.usuario_repository.get_usuario_by_email(email)

        if not usuario or not usuario.senha_hash:
            await self._registrar_audit(
                operacao="LOGIN_FALHA_USUARIO_NAO_ENCONTRADO",
                ip=ip, user_agent=user_agent
            )
            raise EntityNotFoundException("Credenciais inválidas.")

        agora = datetime.now(timezone.utc)

        if usuario.bloqueado_ate and usuario.bloqueado_ate > agora:
            raise BlockedAccountException(
                f"Conta bloqueada. Tente novamente após {usuario.bloqueado_ate.isoformat()}."
            )

        if not verify_password(senha, usuario.senha_hash):
            await self._processar_tentativa_falha(usuario, agora, ip, user_agent)

        await self._resetar_tentativas_falhas(usuario)

        role = await self.role_repository.get_role_by_id(usuario.fk_role)
        if not role:
            raise HTTPException(status_code=500, detail="Papel do usuário não encontrado")

        access_token  = create_access_token(str(usuario.id), role=role.nome)
        refresh_token = create_refresh_token(str(usuario.id))

        ttl   = int(timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS).total_seconds())
        redis = await get_redis()
        await redis.setex(f"{REFRESH_TOKEN_PREFIX}{usuario.id}", ttl, refresh_token)

        await self._registrar_audit(
            operacao="LOGIN_SUCESSO",
            usuario_id=usuario.id, ip=ip, user_agent=user_agent
        )

        return TokenResponse(access_token=access_token, refresh_token=refresh_token)


    async def refresh(self, refresh_token: str) -> TokenResponse:
        payload = self._decode_and_validate_refresh_token(refresh_token)
        user_id = payload["sub"]

        await self._validate_token_rotation(user_id, refresh_token)

        usuario = await self._get_and_validate_active_user(user_id)

        return await self._perform_token_rotation(usuario)

    # ── Privados ──────────────────────────────────────────────────────────────

    async def _registrar_audit(
        self,
        operacao:   str,
        usuario_id  = None,
        ip:         str = None,
        user_agent: str = None,
    ) -> None:
        log = AuditLog(
            fk_usuario     = usuario_id,
            operacao       = operacao,
            tabela_afetada = "usuarios",
            ip_origem      = ip,
            user_agent     = user_agent,
        )
        await self.audit_repository.registrar_log(log)


    async def _processar_tentativa_falha(
        self,
        usuario:    Usuario,
        agora:      datetime,
        ip:         str,
        user_agent: str,
    ) -> None:
        usuario.tentativas_falhas += 1

        if usuario.tentativas_falhas >= MAX_TENTATIVAS:
            usuario.bloqueado_ate  = agora + timedelta(minutes=LOCKOUT_MINUTES)
            usuario.tentativas_falhas = 0

        await self.usuario_repository.atualizar_usuario(usuario)

        await self._registrar_audit(
            operacao   = "LOGIN_FALHA_SENHA_INCORRETA",
            usuario_id = usuario.id,
            ip         = ip,
            user_agent = user_agent,
        )

        raise WrongPasswordException("Credenciais inválidas.")


    async def _resetar_tentativas_falhas(self, usuario: Usuario) -> None:
        if usuario.tentativas_falhas > 0 or usuario.bloqueado_ate is not None:
            usuario.tentativas_falhas = 0
            usuario.bloqueado_ate     = None
            await self.usuario_repository.atualizar_usuario(usuario)


    def _decode_and_validate_refresh_token(self, refresh_token: str) -> dict:
        try:
            payload = decode_token(refresh_token)
        except JWTError:
            raise InvalidTokenException("Refresh token inválido ou expirado.")

        if payload.get("type") != "refresh":
            raise InvalidTokenException("Token inválido.")

        return payload


    async def _validate_token_rotation(self, user_id: str, refresh_token: str) -> None:
        redis  = await get_redis()
        stored = await redis.get(f"{REFRESH_TOKEN_PREFIX}{user_id}")

        if not stored or stored != refresh_token:
            await redis.delete(f"{REFRESH_TOKEN_PREFIX}{user_id}")
            raise InvalidTokenException("Refresh token já utilizado ou revogado.")


    async def _get_and_validate_active_user(self, user_id: str) -> Usuario:
        usuario = await self.usuario_repository.get_usuario_by_id(user_id)

        if not usuario or not usuario.is_active:
            raise InactiveUserException("Usuário inativo.")

        return usuario


    async def _perform_token_rotation(self, usuario: Usuario) -> TokenResponse:
        role = await self.role_repository.get_role_by_id(usuario.fk_role)
        if not role:
            raise InvalidTokenException("Papel do usuário não encontrado.")

        new_access  = create_access_token(str(usuario.id), role=role.nome)
        new_refresh = create_refresh_token(str(usuario.id))

        ttl   = int(timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS).total_seconds())
        redis = await get_redis()
        await redis.setex(f"{REFRESH_TOKEN_PREFIX}{usuario.id}", ttl, new_refresh)

        return TokenResponse(access_token=new_access, refresh_token=new_refresh)
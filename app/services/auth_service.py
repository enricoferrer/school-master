from datetime import datetime, timezone
from jose import JWTError
import redis

from datetime import timedelta

from app.exceptions.EntityNotFoundException import EntityNotFoundException
from app.exceptions.InactiveUserException import InactiveUserException
from app.models.usuario import Usuario
from app.models.audit_log import AuditLog
from app.exceptions.WrongPasswordException import WrongPasswordException
from app.exceptions.InvalidTokenException import InvalidTokenException
from app.exceptions.BlockedAccountException import BlockedAccountException
from app.repositories.audit_repository import AuditRepository
from app.core.security import verify_password, create_access_token, create_refresh_token, decode_token
from app.core.config import settings

from app.repositories.usuario_repository import UsuarioRepository
from app.schemas.auth import TokenResponse

redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

MAX_TENTATIVAS = 5
LOCKOUT_MINUTES = 15
REFRESH_TOKEN_PREFIX = "refresh:"


class AuthService:
    def __init__(self, audit_repository: AuditRepository, usuario_repository: UsuarioRepository):
        self.audit_repository = audit_repository
        self.usuario_repository = usuario_repository

    def _registrar_audit(self, operacao: str, usuario_id=None,
                         ip: str = None, user_agent: str = None):
        log = AuditLog(
            fk_usuario=usuario_id,
            operacao=operacao,
            tabela_afetada="usuarios",
            ip_origem=ip,
            user_agent=user_agent,
        )
        self.audit_repository.registrar_log(log)
        

    def login(self, email: str, senha: str, ip: str, user_agent: str) -> TokenResponse:
        usuario = self.usuario_repository.get_usuario_by_email(email)
        if not usuario or not usuario.senha_hash:
            self._registrar_audit(
                operacao="LOGIN_FALHA_USUARIO_NAO_ENCONTRADO",
                ip=ip, user_agent=user_agent
            )
            raise EntityNotFoundException("Credenciais inválidas.")  

        agora = datetime.now(timezone.utc)
        if usuario.bloqueado_ate and usuario.bloqueado_ate > agora:
            raise BlockedAccountException(f"Conta bloqueada. Tente novamente após {usuario.bloqueado_ate.isoformat()}.")

        if not verify_password(senha, usuario.senha_hash):
            self._processar_tentativa_falha(usuario, agora, ip, user_agent)
        
        self._resetar_tentativas_falhas(usuario)

        access_token = create_access_token(str(usuario.id), role=str(usuario.fk_role))
        refresh_token = create_refresh_token(str(usuario.id))

        ttl = int(timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS).total_seconds())
        redis_client.setex(f"{REFRESH_TOKEN_PREFIX}{usuario.id}", ttl, refresh_token)

        self._registrar_audit(
            operacao="LOGIN_SUCESSO",
            usuario_id=usuario.id, ip=ip, user_agent=user_agent
        )

        return TokenResponse(access_token=access_token, refresh_token=refresh_token)

    def refresh(self, refresh_token: str) -> TokenResponse:
        """Realiza o refresh token com rotation."""
        payload = self._decode_and_validate_refresh_token(refresh_token)
        user_id = payload["sub"]

        self._validate_token_rotation(user_id, refresh_token)

        usuario = self._get_and_validate_active_user(user_id)

        return self._perform_token_rotation(usuario)

    
    def _processar_tentativa_falha(self, usuario: Usuario, agora: datetime, ip: str, user_agent: str) -> None:
        """Incrementa tentativas, bloqueia se necessário e registra auditoria."""
        usuario.tentativas_falhas += 1

        if usuario.tentativas_falhas >= MAX_TENTATIVAS:
            usuario.bloqueado_ate = agora + timedelta(minutes=LOCKOUT_MINUTES)
            usuario.tentativas_falhas = 0

        self.usuario_repository.atualizar_usuario(usuario)

        self._registrar_audit(
            operacao="LOGIN_FALHA_SENHA_INCORRETA",
            usuario_id=usuario.id,
            ip=ip,
            user_agent=user_agent
        )

        raise WrongPasswordException("Credenciais inválidas.")
    
    def _resetar_tentativas_falhas(self, usuario: Usuario) -> None:
        """Reseta tentativas e desbloqueia a conta após login bem-sucedido."""
        if usuario.tentativas_falhas > 0 or usuario.bloqueado_ate is not None:
            usuario.tentativas_falhas = 0
            usuario.bloqueado_ate = None
            self.usuario_repository.atualizar_usuario(usuario)
            
    
    def _decode_and_validate_refresh_token(self, refresh_token: str) -> dict:
        """Decodifica o token e valida se é do tipo 'refresh'."""
        try:
            payload = decode_token(refresh_token)
        except JWTError:
            raise InvalidTokenException("Refresh token inválido ou expirado.")

        if payload.get("type") != "refresh":
            raise InvalidTokenException("Token inválido.")

        return payload


    def _validate_token_rotation(self, user_id: str, refresh_token: str) -> None:
        """Valida o token rotation no Redis. Se inválido, força logout total."""
        stored = redis_client.get(f"{REFRESH_TOKEN_PREFIX}{user_id}")

        if not stored or stored != refresh_token:
            redis_client.delete(f"{REFRESH_TOKEN_PREFIX}{user_id}")
            raise InvalidTokenException("Refresh token já utilizado ou revogado.")


    def _get_and_validate_active_user(self, user_id: str) -> Usuario:
        """Busca o usuário e garante que ele esteja ativo."""
        usuario = self.usuario_repository.get_usuario_by_id(user_id)

        if not usuario or not usuario.is_active:
            raise InactiveUserException("Usuário inativo.")

        return usuario


    def _perform_token_rotation(self, usuario: Usuario) -> TokenResponse:
        """Gera novo par de tokens e atualiza o Redis (token rotation)."""
        new_access = create_access_token(str(usuario.id), role=str(usuario.fk_role))
        new_refresh = create_refresh_token(str(usuario.id))

        ttl = int(timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS).total_seconds())
        redis_client.setex(f"{REFRESH_TOKEN_PREFIX}{usuario.id}", ttl, new_refresh)

        return TokenResponse(access_token=new_access, refresh_token=new_refresh)
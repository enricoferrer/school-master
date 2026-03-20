from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def hash_password(plain: str) -> str:
    if not plain:
        raise ValueError("Senha não pode ser vazia")

    if len(plain.encode("utf-8")) > 72:
        raise ValueError("Senha muito longa (máx 72 bytes para bcrypt)")
    return pwd_context.hash(plain)

def create_access_token(subject: str, role: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": subject, "role": role, "exp": expire, "type": "access"}
    return jwt.encode(payload, settings.JWT_PRIVATE_KEY, algorithm="RS256")

def create_refresh_token(subject: str) -> str:
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {"sub": subject, "exp": expire, "type": "refresh"}
    return jwt.encode(payload, settings.JWT_PRIVATE_KEY, algorithm="RS256")

def decode_token(token: str) -> dict:
    """Lança JWTError se inválido ou expirado."""
    return jwt.decode(token, settings.JWT_PUBLIC_KEY, algorithms=["RS256"])
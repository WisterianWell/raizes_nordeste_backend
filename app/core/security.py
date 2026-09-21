from datetime import datetime, timedelta, timezone
import jwt
from pwdlib import PasswordHash

from app.core.config import get_settings

settings = get_settings()
senha_hash = PasswordHash.recommended()
DUMMY_HASH = senha_hash.hash("dummy_senha")

def get_senha_hash(senha: str) -> str:
    return senha_hash.hash(senha)

def verify_senha(senha: str, hashed_senha: str) -> bool:
    return senha_hash.verify(senha, hashed_senha)

def create_token_acesso(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.jwt_expiration_minutes))
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt

def create_token_refresh(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(days=settings.jwt_refresh_expiration_days))
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt
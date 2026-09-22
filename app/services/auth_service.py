import jwt
from fastapi import status
from jwt.exceptions import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cliente import Cliente
from app.models.funcionario import Funcionario
from app.repositories.cliente_repo import ClienteRepository
from app.repositories.funcionario_repo import FuncionarioRepository
from app.enums import AcaoAuditoria, TipoUsuario
from app.core.config import get_settings
from app.exceptions.error_codes import ErrorCodes
from app.exceptions.exceptions import AppException
from app.core.security import verify_senha, create_token_acesso, create_token_refresh, DUMMY_HASH
from app.schemas.auth_schemas import TokenResponse
from app.services.auditoria_service import registrar_log

settings = get_settings()

credentials_exception = AppException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    error_code=ErrorCodes.REFRESH_TOKEN_INVALIDO,
    message="Refresh token inválido ou expirado.",
    headers={"WWW-Authenticate": "Bearer"}
)

class AuthService:
    def __init__(self, session: AsyncSession):
        self.cliente_repo = ClienteRepository(session)
        self.funcionario_repo = FuncionarioRepository(session)

    async def authenticate_cliente(self, email: str, senha: str) -> Cliente | None:
        cliente = await self.cliente_repo.get_by_email(email)
        if not cliente:
            verify_senha(senha, DUMMY_HASH)
            return None
        if not verify_senha(senha, cliente.hashed_senha):
            return None
        return cliente

    async def authenticate_funcionario(self, email: str, senha: str) -> Funcionario | None:
        funcionario = await self.funcionario_repo.get_by_email(email)
        if not funcionario:
            verify_senha(senha, DUMMY_HASH)
            return None
        if not verify_senha(senha, funcionario.hashed_senha):
            return None
        return funcionario

    def _build_tokens(self, sub: str, role: str) -> TokenResponse:
        access_token = create_token_acesso({"sub": sub, "role": role})
        refresh_token = create_token_refresh({"sub": sub, "role": role})
        return TokenResponse(access_token=access_token, refresh_token=refresh_token, token_type="bearer")

    async def login(self, email: str, senha: str) -> TokenResponse:
        cliente = await self.authenticate_cliente(email, senha)
        if cliente:
            await registrar_log(
                AcaoAuditoria.LOGIN_SUCESSO, "AUTH", usuario=cliente, id_entidade=cliente.id_cliente
            )
            return self._build_tokens(str(cliente.id_cliente), TipoUsuario.CLIENTE.value)
        funcionario = await self.authenticate_funcionario(email, senha)
        if funcionario:
            await registrar_log(
                AcaoAuditoria.LOGIN_SUCESSO, "AUTH", usuario=funcionario, id_entidade=funcionario.id_funcionario
            )
            return self._build_tokens(str(funcionario.id_funcionario), TipoUsuario.FUNCIONARIO.value)
        await registrar_log(AcaoAuditoria.LOGIN_FALHA, "AUTH", detalhes={"email": email})
        raise AppException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code=ErrorCodes.CREDENCIAIS_INVALIDAS,
            message="Email ou senha inválidos.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    async def refresh(self, refresh_token: str) -> TokenResponse:
        try:
            payload = jwt.decode(refresh_token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        except InvalidTokenError:
            raise credentials_exception
        if payload.get("type") != "refresh":
            raise credentials_exception
        sub = payload.get("sub")
        role = payload.get("role")
        if sub is None or role is None:
            raise credentials_exception
        if role == TipoUsuario.FUNCIONARIO.value:
            usuario = await self.funcionario_repo.get_by_id(int(sub))
        else:
            usuario = await self.cliente_repo.get_by_id(int(sub))
        if usuario is None:
            raise credentials_exception
        return self._build_tokens(sub, role)

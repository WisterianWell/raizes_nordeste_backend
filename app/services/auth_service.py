from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cliente import Cliente
from app.models.funcionario import Funcionario
from app.repositories.cliente_repo import ClienteRepository
from app.repositories.funcionario_repo import FuncionarioRepository
from app.repositories.enums import TipoUsuario
from app.core.security import verify_senha, create_token_acesso, DUMMY_HASH
from app.schemas.auth_schemas import TokenResponse

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

    async def login(self, email: str, senha: str) -> TokenResponse:
        cliente = await self.authenticate_cliente(email, senha)
        if cliente:
            access_token = create_token_acesso({"sub": str(cliente.id_cliente), "role": TipoUsuario.CLIENTE.value})
            return TokenResponse(access_token=access_token, token_type="bearer")
        funcionario = await self.authenticate_funcionario(email, senha)
        if funcionario:
            access_token = create_token_acesso({"sub": str(funcionario.id_funcionario), "role": TipoUsuario.FUNCIONARIO.value})
            return TokenResponse(access_token=access_token, token_type="bearer")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos.",
            headers={"WWW-Authenticate": "Bearer"}
        )

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cliente import Cliente
from app.repositories.cliente_repo import ClienteRepository
from app.repositories.enums import TipoUsuario
from app.core.security import verify_senha, create_token_acesso, DUMMY_HASH
from app.schemas.auth_schemas import TokenResponse

class AuthService:
    def __init__(self, session: AsyncSession):
        self.repo = ClienteRepository(session)

    async def authenticate_cliente(self, email: str, senha: str) -> Cliente | None:
        cliente = await self.repo.get_by_email(email)
        if not cliente:
            verify_senha(senha, DUMMY_HASH)
            return None
        if not verify_senha(senha, cliente.hashed_senha):
            return None
        return cliente

    async def login(self, email: str, senha: str) -> TokenResponse:
        cliente = await self.authenticate_cliente(email, senha)
        if not cliente:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou senha incorretos.",
                headers={"WWW-Authenticate": "Bearer"}
            )

        access_token = create_token_acesso({"sub": str(cliente.id_cliente), "role": TipoUsuario.CLIENTE.value})
        return TokenResponse(access_token=access_token, token_type="bearer")

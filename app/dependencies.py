from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.database import get_db_session
from app.models.cliente import Cliente
from app.repositories.cliente_repo import ClienteRepository
from app.schemas.auth_schemas import TokenData

settings = get_settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="v1/auth/login")

async def get_current_usuario(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> Cliente:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
        id_cliente = payload.get("sub")
        if id_cliente is None:
            raise credentials_exception
        token_data = TokenData(id_cliente=id_cliente)
    except InvalidTokenError:
        raise credentials_exception
    cliente = await ClienteRepository(db).get_by_id(int(token_data.id_cliente))
    if cliente is None:
        raise credentials_exception
    return cliente

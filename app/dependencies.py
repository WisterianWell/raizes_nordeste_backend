from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.database import get_db_session
from app.models.cliente import Cliente
from app.models.funcionario import Funcionario
from app.repositories.cliente_repo import ClienteRepository
from app.repositories.funcionario_repo import FuncionarioRepository
from app.repositories.enums import CargoFunc, TipoUsuario
from app.schemas.auth_schemas import TokenData

settings = get_settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="v1/auth/login")

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Não foi possível validar as credenciais.",
    headers={"WWW-Authenticate": "Bearer"},
)

async def get_current_usuario(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> Cliente | Funcionario:
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        sub = payload.get("sub")
        role = payload.get("role")
        if sub is None or role is None:
            raise credentials_exception
        token_data = TokenData(sub=sub, role=role)
    except InvalidTokenError:
        raise credentials_exception
    if token_data.role == TipoUsuario.FUNCIONARIO.value:
        usuario = await FuncionarioRepository(db).get_by_id(int(token_data.sub))
    else:
        usuario = await ClienteRepository(db).get_by_id(int(token_data.sub))
    if usuario is None:
        raise credentials_exception
    return usuario

def requer_cargo(*cargos_permitidos: CargoFunc):
    valores_permitidos = [cargo.value for cargo in cargos_permitidos]
    async def _checar(
        current_usuario: Annotated[Cliente | Funcionario, Depends(get_current_usuario)],
    ) -> Funcionario:
        if not isinstance(current_usuario, Funcionario):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso restrito a funcionários.",
            )
        if current_usuario.cargo not in valores_permitidos:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não tem permissão para acessar este recurso.",
            )
        return current_usuario
    return _checar

def requer_cliente_ou_cargo(*cargos_permitidos: CargoFunc):
    checar_perfil = requer_cargo(*cargos_permitidos)
    async def _checar(
        id_cliente: int,
        current_usuario: Annotated[Cliente | Funcionario, Depends(get_current_usuario)],
    ) -> Cliente | Funcionario:
        if isinstance(current_usuario, Cliente):
            if current_usuario.id_cliente != id_cliente:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Você só pode acessar a sua própria conta.",
                )
            return current_usuario
        return await checar_perfil(current_usuario)
    return _checar

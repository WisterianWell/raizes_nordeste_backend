from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db_session
from app.schemas.auth_schemas import RefreshRequest, TokenResponse
from app.services.auth_service import AuthService

router = APIRouter()

def get_auth_service(db: Annotated[AsyncSession, Depends(get_db_session)]) -> AuthService:
    return AuthService(db)

@router.post("/login")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> TokenResponse:
    return await service.login(email=form_data.username, senha=form_data.password)

@router.post("/refresh")
async def refresh(
    data: RefreshRequest,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> TokenResponse:
    return await service.refresh(data.refresh_token)

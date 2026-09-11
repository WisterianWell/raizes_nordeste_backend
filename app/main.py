from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy import select

from app.core.config import get_settings, Settings
from app.core.security import get_senha_hash
from app.database import sessionmanager
from app.models.base import Base
from app.models.funcionario import Funcionario
from app.enums import CargoFunc
from app.repositories.funcionario_repo import FuncionarioRepository
from app.api.router import api_router

async def create_admin(settings: Settings) -> None:
    if not settings.admin_email or not settings.admin_senha:
        return

    async with sessionmanager.session() as session:
        repo = FuncionarioRepository(session)
        result = await session.execute(
            select(Funcionario.id_funcionario)
            .where(Funcionario.cargo == CargoFunc.ADMIN.value)
            .limit(1)
        )
        if result.scalar_one_or_none() is not None:
            return
        await repo.create(
            nome=settings.admin_nome,
            email=settings.admin_email,
            cpf=settings.admin_cpf,
            telefone=settings.admin_telefone,
            hashed_senha=get_senha_hash(settings.admin_senha),
            cargo=CargoFunc.ADMIN.value,
        )

@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    await sessionmanager.init(settings.database_url)
    await sessionmanager.create_all(Base)
    await create_admin(settings)
    yield
    await sessionmanager.close()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        lifespan=lifespan,
    )
    app.include_router(api_router)

    @app.get("/health", summary="verfica a saúde da API")
    async def health_check() -> dict:
        return {"status": "ok"}
    return app

app = create_app()

from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.core.config import get_settings
from app.database import sessionmanager
from app.models.base import Base
from app.api.router import api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()

    await sessionmanager.init(settings.database_url)
    await sessionmanager.create_all(Base)
    yield

    await sessionmanager.close()


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        lifespan=lifespan
    )

    app.include_router(api_router)

    @app.get("/health", summary="verfica a saúde da API")
    async def health_check() -> dict:
        return {"status": "ok"}

    return app

app = create_app()

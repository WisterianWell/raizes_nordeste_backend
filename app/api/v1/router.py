from fastapi import APIRouter

from app.api.v1.routers import clientes


# Agregador de routers da API v1
api_router = APIRouter()
api_router.include_router(clientes.router, prefix="/clientes", tags=["clientes"])
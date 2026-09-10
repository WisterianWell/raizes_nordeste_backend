from fastapi import APIRouter
from app.api.v1.routers import clientes, auth, funcionarios

# Agregador de routers da API v1
router = APIRouter()
router.include_router(clientes.router, prefix="/clientes", tags=["clientes"])
router.include_router(funcionarios.router, prefix="/funcionarios", tags=["funcionarios"])
router.include_router(auth.router, prefix="/auth", tags=["auth"])

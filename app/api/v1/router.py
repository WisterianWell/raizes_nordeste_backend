from fastapi import APIRouter
from app.api.v1.routers import cardapios, clientes, auth, funcionarios, produtos, unidades

# Agregador de routers da API v1
router = APIRouter()
router.include_router(clientes.router, prefix="/clientes", tags=["clientes"])
router.include_router(funcionarios.router, prefix="/funcionarios", tags=["funcionarios"])
router.include_router(unidades.router, prefix="/unidades", tags=["unidades"])
router.include_router(produtos.router, prefix="/produtos", tags=["produtos"])
router.include_router(cardapios.router, prefix="/cardapios", tags=["cardapios"])
router.include_router(auth.router, prefix="/auth", tags=["auth"])

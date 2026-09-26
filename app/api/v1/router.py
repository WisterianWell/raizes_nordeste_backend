from fastapi import APIRouter
from app.api.v1.routers import auditoria, cardapio, clientes, auth, estoque, fidelizacao, funcionarios, pagamentos, pedidos, produtos, promocoes, unidades

# Agregador de routers da API v1
router = APIRouter()
router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(clientes.router, prefix="/clientes", tags=["clientes"])
router.include_router(funcionarios.router, prefix="/funcionarios", tags=["funcionarios"])
router.include_router(unidades.router, prefix="/unidades", tags=["unidades"])
router.include_router(produtos.router, prefix="/produtos", tags=["produtos"])
router.include_router(cardapio.router, prefix="/cardapios", tags=["cardapios"])
router.include_router(promocoes.router, prefix="/promocoes", tags=["promocoes"])
router.include_router(estoque.router, prefix="/estoque", tags=["estoque"])
router.include_router(fidelizacao.router, prefix="/fidelizacao", tags=["fidelizacao"])
router.include_router(pedidos.router, prefix="/pedidos", tags=["pedidos"])
router.include_router(pagamentos.router, prefix="/pagamentos", tags=["pagamentos"])
router.include_router(auditoria.router, prefix="/auditoria", tags=["auditoria"])

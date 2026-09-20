from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import requer_cargo
from app.database import get_db_session
from app.models.funcionario import Funcionario
from app.cargos import CARGOS_ADMIN
from app.schemas.cardapio_schemas import CardapioResponse
from app.schemas.mov_estoque_schemas import MovEstoqueRequest, MovEstoqueResponse
from app.services.estoque_service import EstoqueService

router = APIRouter()

def get_estoque_service(db: Annotated[AsyncSession, Depends(get_db_session)]) -> EstoqueService:
    return EstoqueService(db)

@router.get("/")
async def get_estoque_by_unidade(
    id_unidade: int,
    service: Annotated[EstoqueService, Depends(get_estoque_service)],
    current_usuario: Annotated[Funcionario, Depends(
        requer_cargo(*CARGOS_ADMIN)
        )],
    offset: int = 0,
    limit: int = 10,
) -> list[CardapioResponse]:
    return await service.get_estoque_by_unidade(id_unidade, offset, limit)

@router.post("/entrada")
async def criar_entrada_estoque(
    data: MovEstoqueRequest,
    service: Annotated[EstoqueService, Depends(get_estoque_service)],
    current_usuario: Annotated[Funcionario, Depends(
        requer_cargo(*CARGOS_ADMIN)
        )],
) -> list[MovEstoqueResponse]:
    return await service.dar_entrada(data)

@router.post("/saida")
async def criar_saida_estoque(
    data: MovEstoqueRequest,
    service: Annotated[EstoqueService, Depends(get_estoque_service)],
    current_usuario: Annotated[Funcionario, Depends(
        requer_cargo(*CARGOS_ADMIN)
        )],
) -> list[MovEstoqueResponse]:
    return await service.dar_saida(data)

@router.get("/{id_unidade}/movimentacoes")
async def get_movimentacoes_estoque(
    id_unidade: int,
    service: Annotated[EstoqueService, Depends(get_estoque_service)],
    current_usuario: Annotated[Funcionario, Depends(
        requer_cargo(*CARGOS_ADMIN)
        )],
    id_produto: int | None = None,
    offset: int = 0,
    limit: int = 10,
) -> list[MovEstoqueResponse]:
    return await service.get_movimentacoes(id_unidade, id_produto, offset, limit)

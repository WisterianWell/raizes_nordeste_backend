from typing import Annotated
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import requer_cargo
from app.database import get_db_session
from app.models.funcionario import Funcionario
from app.cargos import CARGOS_ADMIN
from app.schemas.cardapio_schemas import (
    CardapioPublicoResponse,
    CardapioRequest,
    CardapioResponse,
    CardapioUpdate,
)
from app.services.cardapio_service import CardapioService

router = APIRouter()

def get_cardapio_service(db: Annotated[AsyncSession, Depends(get_db_session)]) -> CardapioService:
    return CardapioService(db)

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_cardapio_item(
    data: CardapioRequest,
    service: Annotated[CardapioService, Depends(get_cardapio_service)],
    current_usuario: Annotated[Funcionario, Depends(
        requer_cargo(*CARGOS_ADMIN)
        )],
) -> CardapioResponse:
    return await service.create_cardapio(data)

@router.get("/")
async def get_cardapio_by_unidade(
    id_unidade: int,
    service: Annotated[CardapioService, Depends(get_cardapio_service)],
    offset: int = 0,
    limit: int = 10,
) -> list[CardapioPublicoResponse]:
    return await service.get_cardapio_by_unidade(id_unidade, offset, limit, apenas_disponiveis=True)

@router.get("/{id_produto}/{id_unidade}")
async def get_cardapio_item(
    id_produto: int,
    id_unidade: int,
    service: Annotated[CardapioService, Depends(get_cardapio_service)],
    current_usuario: Annotated[Funcionario, Depends(
        requer_cargo(*CARGOS_ADMIN)
        )],
) -> CardapioResponse:
    return await service.get_item(id_produto, id_unidade)

@router.patch("/{id_produto}/{id_unidade}")
async def update_cardapio_item(
    id_produto: int,
    id_unidade: int,
    data: CardapioUpdate,
    service: Annotated[CardapioService, Depends(get_cardapio_service)],
    current_usuario: Annotated[Funcionario, Depends(
        requer_cargo(*CARGOS_ADMIN)
        )],
) -> CardapioResponse:
    return await service.update_item(id_produto, id_unidade, data)

@router.delete("/{id_produto}/{id_unidade}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cardapio_item(
    id_produto: int,
    id_unidade: int,
    service: Annotated[CardapioService, Depends(get_cardapio_service)],
    current_usuario: Annotated[Funcionario, Depends(
        requer_cargo(*CARGOS_ADMIN)
        )],
):
    await service.delete_item(id_produto, id_unidade)

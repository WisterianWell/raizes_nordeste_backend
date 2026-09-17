from typing import Annotated
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import requer_cargo
from app.database import get_db_session
from app.models.funcionario import Funcionario
from app.enums import CargoFunc
from app.schemas.produto_schemas import ProdutoRequest, ProdutoResponse, ProdutoUpdate
from app.services.produto_service import ProdutoService

router = APIRouter()

def get_produto_service(db: Annotated[AsyncSession, Depends(get_db_session)]) -> ProdutoService:
    return ProdutoService(db)

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_produto(
    data: ProdutoRequest,
    service: Annotated[ProdutoService, Depends(get_produto_service)],
    current_usuario: Annotated[Funcionario, Depends(
        requer_cargo(CargoFunc.ADMIN, CargoFunc.GERENTE)
        )],
) -> ProdutoResponse:
    return await service.create_produto(data)

@router.get("/{id_produto}")
async def get_produto_by_id(
    id_produto: int,
    service: Annotated[ProdutoService, Depends(get_produto_service)],
    current_usuario: Annotated[Funcionario, Depends(
        requer_cargo(CargoFunc.ADMIN, CargoFunc.GERENTE)
        )],
) -> ProdutoResponse:
    return await service.get_produto_by_id(id_produto)

@router.get("/")
async def get_produtos(
    service: Annotated[ProdutoService, Depends(get_produto_service)],
    current_usuario: Annotated[Funcionario, Depends(
        requer_cargo(CargoFunc.ADMIN, CargoFunc.GERENTE)
        )],
    categoria: str | None = None,
    offset: int = 0,
    limit: int = 100,
) -> list[ProdutoResponse]:
    return await service.get_produtos(categoria, offset, limit)

@router.patch("/{id_produto}")
async def update_produto(
    id_produto: int,
    data: ProdutoUpdate,
    service: Annotated[ProdutoService, Depends(get_produto_service)],
    current_usuario: Annotated[Funcionario, Depends(
        requer_cargo(CargoFunc.ADMIN, CargoFunc.GERENTE)
        )],
) -> ProdutoResponse:
    return await service.update_produto(id_produto, data)

@router.delete("/{id_produto}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_produto(
    id_produto: int,
    service: Annotated[ProdutoService, Depends(get_produto_service)],
    current_usuario: Annotated[Funcionario, Depends(
        requer_cargo(CargoFunc.ADMIN, CargoFunc.GERENTE)
        )],
):
    await service.delete_produto(id_produto)

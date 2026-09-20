from typing import Annotated
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import requer_cargo
from app.database import get_db_session
from app.models.funcionario import Funcionario
from app.cargos import CARGOS_ADMIN
from app.schemas.promocao_schemas import PromocaoRequest, PromocaoResponse, PromocaoUpdate
from app.services.promocao_service import PromocaoService

router = APIRouter()

def get_promocao_service(db: Annotated[AsyncSession, Depends(get_db_session)]) -> PromocaoService:
    return PromocaoService(db)

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_promocao(
    data: PromocaoRequest,
    service: Annotated[PromocaoService, Depends(get_promocao_service)],
    current_usuario: Annotated[Funcionario, Depends(
        requer_cargo(*CARGOS_ADMIN)
        )],
) -> PromocaoResponse:
    return await service.create_promocao(data)

@router.get("/")
async def get_promocoes(
    service: Annotated[PromocaoService, Depends(get_promocao_service)],
    id_produto: int | None = None,
    id_unidade: int | None = None,
    ativo: bool | None = None,
    offset: int = 0,
    limit: int = 10,
) -> list[PromocaoResponse]:
    return await service.get_promocoes(id_produto, id_unidade, ativo, offset, limit)

@router.get("/{id_promocao}")
async def get_promocao_by_id(
    id_promocao: int,
    service: Annotated[PromocaoService, Depends(get_promocao_service)],
) -> PromocaoResponse:
    return await service.get_promocao_by_id(id_promocao)

@router.patch("/{id_promocao}")
async def update_promocao(
    id_promocao: int,
    data: PromocaoUpdate,
    service: Annotated[PromocaoService, Depends(get_promocao_service)],
    current_usuario: Annotated[Funcionario, Depends(
        requer_cargo(*CARGOS_ADMIN)
        )],
) -> PromocaoResponse:
    return await service.update_promocao(id_promocao, data)

@router.delete("/{id_promocao}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_promocao(
    id_promocao: int,
    service: Annotated[PromocaoService, Depends(get_promocao_service)],
    current_usuario: Annotated[Funcionario, Depends(
        requer_cargo(*CARGOS_ADMIN)
        )],
):
    await service.delete_promocao(id_promocao)

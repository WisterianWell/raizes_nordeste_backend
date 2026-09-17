from typing import Annotated
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import requer_cargo
from app.database import get_db_session
from app.models.funcionario import Funcionario
from app.cargos import CARGOS_ADMIN
from app.schemas.unidade_schemas import UnidadeRequest, UnidadeResponse, UnidadeUpdate
from app.services.unidade_service import UnidadeService

router = APIRouter()

def get_unidade_service(db: Annotated[AsyncSession, Depends(get_db_session)]) -> UnidadeService:
    return UnidadeService(db)

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_unidade(
    data: UnidadeRequest,
    service: Annotated[UnidadeService, Depends(get_unidade_service)],
    current_usuario: Annotated[Funcionario, Depends(
        requer_cargo(*CARGOS_ADMIN)
        )],
) -> UnidadeResponse:
    return await service.create_unidade(data)

@router.get("/{id_unidade}")
async def get_unidade_by_id(
    id_unidade: int,
    service: Annotated[UnidadeService, Depends(get_unidade_service)],
    current_usuario: Annotated[Funcionario, Depends(
        requer_cargo(*CARGOS_ADMIN)
        )],
) -> UnidadeResponse:
    return await service.get_unidade_by_id(id_unidade)

@router.get("/")
async def get_all_unidades(
    service: Annotated[UnidadeService, Depends(get_unidade_service)],
    current_usuario: Annotated[Funcionario, Depends(
        requer_cargo(*CARGOS_ADMIN)
        )],
    offset: int = 0,
    limit: int = 10,
) -> list[UnidadeResponse]:
    return await service.get_all_unidades(offset, limit)

@router.patch("/{id_unidade}")
async def update_unidade(
    id_unidade: int,
    data: UnidadeUpdate,
    service: Annotated[UnidadeService, Depends(get_unidade_service)],
    current_usuario: Annotated[Funcionario, Depends(
        requer_cargo(*CARGOS_ADMIN)
        )],
) -> UnidadeResponse:
    return await service.update_unidade(id_unidade, data)

@router.delete("/{id_unidade}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_unidade(
    id_unidade: int,
    service: Annotated[UnidadeService, Depends(get_unidade_service)],
    current_usuario: Annotated[Funcionario, Depends(
        requer_cargo(*CARGOS_ADMIN)
        )],
):
    await service.delete_unidade(id_unidade)

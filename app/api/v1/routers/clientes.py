from typing import Annotated
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_usuario, requer_cargo, requer_cliente_ou_cargo
from app.database import get_db_session
from app.models.cliente import Cliente
from app.models.funcionario import Funcionario
from app.repositories.enums import CargoFunc
from app.schemas.cliente_schemas import ClienteRequest, ClienteResponse, ClienteUpdate
from app.services.cliente_service import ClienteService

router = APIRouter()

def get_cliente_service(db: Annotated[AsyncSession, Depends(get_db_session)]) -> ClienteService:
    return ClienteService(db)

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_cliente(
    data: ClienteRequest,
    service: Annotated[ClienteService, Depends(get_cliente_service)],
) -> ClienteResponse:
    return await service.create_cliente(data)

@router.get("/{id_cliente}")
async def get_cliente_by_id(
    id_cliente: int,
    service: Annotated[ClienteService, Depends(get_cliente_service)],
    current_usuario: Annotated[Funcionario, Depends(
        requer_cargo(CargoFunc.ATENDENTE, CargoFunc.ADMIN, CargoFunc.GERENTE)
        )],
) -> ClienteResponse:
    return await service.get_cliente_by_id(id_cliente)

@router.get("/")
async def get_all_clientes(
    service: Annotated[ClienteService, Depends(get_cliente_service)],
    current_usuario: Annotated[Funcionario, Depends(
        requer_cargo(CargoFunc.ADMIN, CargoFunc.GERENTE)
        )],
    offset: int = 0,
    limit: int = 100,
) -> list[ClienteResponse]:
    return await service.get_all_clientes(offset, limit)

@router.patch("/{id_cliente}")
async def update_cliente(
    id_cliente: int,
    data: ClienteUpdate,
    service: Annotated[ClienteService, Depends(get_cliente_service)],
    current_usuario: Annotated[Cliente, Depends(get_current_usuario)],
) -> ClienteResponse:
    return await service.update_cliente(id_cliente, data)

@router.delete("/{id_cliente}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cliente(
    id_cliente: int,
    service: Annotated[ClienteService, Depends(get_cliente_service)],
    current_usuario: Annotated[Cliente | Funcionario, Depends(
        requer_cliente_ou_cargo(CargoFunc.ADMIN, CargoFunc.GERENTE)
        )],
):
    await service.delete_cliente(id_cliente)

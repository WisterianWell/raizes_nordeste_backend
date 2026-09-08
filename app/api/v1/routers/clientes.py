from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db_session
from app.schemas.cliente_schemas import ClienteRequest, ClienteResponse, ClienteUpdate
from app.services.cliente_service import ClienteService

router = APIRouter()

def get_cliente_service(db: AsyncSession = Depends(get_db_session)) -> ClienteService:
    return ClienteService(db)

@router.post("/", response_model=ClienteResponse, status_code=status.HTTP_201_CREATED)
async def create_cliente(
    data: ClienteRequest,
    service: ClienteService = Depends(get_cliente_service)
):
    return await service.create_cliente(data)

@router.get("/{id_cliente}", response_model=ClienteResponse)
async def get_cliente_by_id(
    id_cliente: int,
    service: ClienteService = Depends(get_cliente_service)
):
    return await service.get_cliente_by_id(id_cliente)

@router.get("/", response_model=list[ClienteResponse])
async def get_all_clientes(
    offset: int = 0,
    limit: int = 100,
    service: ClienteService = Depends(get_cliente_service)
):
    return await service.get_all_clientes(offset, limit)

@router.patch("/{id_cliente}", response_model=ClienteResponse)
async def update_cliente(
    id_cliente: int,
    data: ClienteUpdate,
    service: ClienteService = Depends(get_cliente_service)
):
    return await service.update_cliente(id_cliente, data)

@router.delete("/{id_cliente}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cliente(
    id_cliente: int,
    service: ClienteService = Depends(get_cliente_service)
):
    await service.delete_cliente(id_cliente)

from typing import Annotated
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_usuario, requer_cargo
from app.database import get_db_session
from app.models.cliente import Cliente
from app.models.funcionario import Funcionario
from app.enums import CanalPedido, CargoFunc
from app.schemas.pagamento_schemas import PagamentoRequest, PagamentoResponse
from app.schemas.pedido_schemas import PedidoRequest, PedidoResponse
from app.services.pagamento_service import PagamentoService
from app.services.pedido_service import PedidoService

router = APIRouter()

def get_pedido_service(db: Annotated[AsyncSession, Depends(get_db_session)]) -> PedidoService:
    return PedidoService(db)

def get_pagamento_service(db: Annotated[AsyncSession, Depends(get_db_session)]) -> PagamentoService:
    return PagamentoService(db)

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_pedido(
    data: PedidoRequest,
    service: Annotated[PedidoService, Depends(get_pedido_service)],
    current_usuario: Annotated[Cliente | Funcionario, Depends(get_current_usuario)],
) -> PedidoResponse:
    return await service.create_pedido(data, current_usuario)

@router.get("/")
async def get_pedidos(
    service: Annotated[PedidoService, Depends(get_pedido_service)],
    current_usuario: Annotated[Cliente | Funcionario, Depends(get_current_usuario)],
    id_cliente: int | None = None,
    id_unidade: int | None = None,
    canal: CanalPedido | None = None,
    offset: int = 0,
    limit: int = 100,
) -> list[PedidoResponse]:
    return await service.get_pedidos(
        current_usuario,
        id_cliente=id_cliente,
        id_unidade=id_unidade,
        canal=canal.value if canal else None,
        offset=offset,
        limit=limit,
    )

@router.get("/{id_pedido}")
async def get_pedido_by_id(
    id_pedido: int,
    service: Annotated[PedidoService, Depends(get_pedido_service)],
    current_usuario: Annotated[Cliente | Funcionario, Depends(get_current_usuario)],
) -> PedidoResponse:
    return await service.get_pedido_by_id(id_pedido, current_usuario)

@router.patch("/{id_pedido}/avancar")
async def avancar_status_pedido(
    id_pedido: int,
    service: Annotated[PedidoService, Depends(get_pedido_service)],
    current_usuario: Annotated[Funcionario, Depends(
        requer_cargo(CargoFunc.ADMIN, CargoFunc.GERENTE, CargoFunc.ATENDENTE, CargoFunc.COZINHA)
        )],
) -> PedidoResponse:
    return await service.avancar_status_pedido(id_pedido)

@router.patch("/{id_pedido}/cancelar")
async def cancelar_pedido(
    id_pedido: int,
    service: Annotated[PedidoService, Depends(get_pedido_service)],
    current_usuario: Annotated[Cliente | Funcionario, Depends(get_current_usuario)],
) -> PedidoResponse:
    return await service.cancelar_pedido(id_pedido, current_usuario)

@router.post("/{id_pedido}/pagar", status_code=status.HTTP_201_CREATED)
async def pagar_pedido(
    id_pedido: int,
    data: PagamentoRequest,
    service: Annotated[PagamentoService, Depends(get_pagamento_service)],
    current_usuario: Annotated[Cliente | Funcionario, Depends(get_current_usuario)],
) -> PagamentoResponse:
    return await service.pagar_pedido(id_pedido, data, current_usuario)

@router.get("/{id_pedido}/pagamentos")
async def get_pagamentos_by_pedido(
    id_pedido: int,
    service: Annotated[PagamentoService, Depends(get_pagamento_service)],
    current_usuario: Annotated[Cliente | Funcionario, Depends(get_current_usuario)],
    offset: int = 0,
    limit: int = 100,
) -> list[PagamentoResponse]:
    return await service.get_pagamentos_by_pedido(id_pedido, current_usuario, offset, limit)

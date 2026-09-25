from typing import Annotated
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_usuario
from app.database import get_db_session
from app.gateways.pagamento import GatewayPagamentoMock, get_gateway_pagamento
from app.models.cliente import Cliente
from app.models.funcionario import Funcionario
from app.schemas.pagamento_schemas import PagamentoRequest, PagamentoResponse
from app.services.pagamento_service import PagamentoService

router = APIRouter()

def get_pagamento_service(
    db: Annotated[AsyncSession, Depends(get_db_session)],
    gateway: Annotated[GatewayPagamentoMock, Depends(get_gateway_pagamento)],
) -> PagamentoService:
    return PagamentoService(db, gateway)

@router.post("/{id_pedido}", status_code=status.HTTP_201_CREATED)
async def pagar_pedido(
    id_pedido: int,
    data: PagamentoRequest,
    service: Annotated[PagamentoService, Depends(get_pagamento_service)],
    current_usuario: Annotated[Cliente | Funcionario, Depends(get_current_usuario)],
) -> PagamentoResponse:
    return await service.pagar_pedido(id_pedido, data, current_usuario)

@router.get("/{id_pedido}")
async def get_pagamentos_by_pedido(
    id_pedido: int,
    service: Annotated[PagamentoService, Depends(get_pagamento_service)],
    current_usuario: Annotated[Cliente | Funcionario, Depends(get_current_usuario)],
    offset: int = 0,
    limit: int = 10,
) -> list[PagamentoResponse]:
    return await service.get_pagamentos_by_pedido(id_pedido, current_usuario, offset, limit)

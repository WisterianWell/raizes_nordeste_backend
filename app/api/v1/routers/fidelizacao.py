from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_usuario, requer_cliente_ou_cargo
from app.database import get_db_session
from app.models.cliente import Cliente
from app.models.funcionario import Funcionario
from app.cargos import CARGOS_ATENDIMENTO
from app.schemas.fidelizacao_schemas import FidelizacaoResponse, MovPontosResponse
from app.services.fidelizacao_service import FidelizacaoService

router = APIRouter()

def get_fidelizacao_service(db: Annotated[AsyncSession, Depends(get_db_session)]) -> FidelizacaoService:
    return FidelizacaoService(db)

@router.post("/termos", status_code=status.HTTP_201_CREATED)
async def aceitar_termos_fidelizacao(
    service: Annotated[FidelizacaoService, Depends(get_fidelizacao_service)],
    current_usuario: Annotated[Cliente | Funcionario, Depends(get_current_usuario)],
) -> FidelizacaoResponse:
    if not isinstance(current_usuario, Cliente):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas clientes podem aceitar os termos de fidelização."
        )
    return await service.aceitar_termos(current_usuario.id_cliente)

@router.get("/{id_cliente}")
async def get_fidelizacao(
    id_cliente: int,
    service: Annotated[FidelizacaoService, Depends(get_fidelizacao_service)],
    current_usuario: Annotated[Cliente | Funcionario, Depends(
        requer_cliente_ou_cargo(*CARGOS_ATENDIMENTO)
        )],
) -> FidelizacaoResponse:
    return await service.get_fidelizacao(id_cliente)

@router.get("/{id_cliente}/movimentacoes")
async def get_movimentacoes_pontos(
    id_cliente: int,
    service: Annotated[FidelizacaoService, Depends(get_fidelizacao_service)],
    current_usuario: Annotated[Cliente | Funcionario, Depends(
        requer_cliente_ou_cargo(*CARGOS_ATENDIMENTO)
        )],
    offset: int = 0,
    limit: int = 10,
) -> list[MovPontosResponse]:
    return await service.get_movimentacoes(id_cliente, offset, limit)

from typing import Annotated
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_usuario, requer_cliente_ou_cargo
from app.database import get_db_session
from app.domain.enums import AcaoAuditoria
from app.models.cliente import Cliente
from app.models.funcionario import Funcionario
from app.domain.cargos import CARGOS_ATENDIMENTO
from app.schemas.fidelizacao_schemas import FidelizacaoResponse, MovPontosResponse
from app.exceptions.error_codes import ErrorCodes
from app.exceptions.exceptions import AppException
from app.services.auditoria_service import registrar_log
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
        raise AppException(
            status_code=status.HTTP_403_FORBIDDEN,
            error_code=ErrorCodes.APENAS_CLIENTE,
            message="Apenas clientes podem aceitar os termos de fidelização."
        )
    resultado = await service.aceitar_termos(current_usuario.id_cliente)
    await registrar_log(
        AcaoAuditoria.CONSENTIMENTO_ACEITO, "FIDELIZACAO",
        usuario=current_usuario, id_entidade=current_usuario.id_cliente,
    )
    return resultado

@router.post("/termos/revogar")
async def revogar_termos_fidelizacao(
    service: Annotated[FidelizacaoService, Depends(get_fidelizacao_service)],
    current_usuario: Annotated[Cliente | Funcionario, Depends(get_current_usuario)],
) -> FidelizacaoResponse:
    if not isinstance(current_usuario, Cliente):
        raise AppException(
            status_code=status.HTTP_403_FORBIDDEN,
            error_code=ErrorCodes.APENAS_CLIENTE,
            message="Apenas clientes podem revogar os termos de fidelização."
        )
    resultado = await service.revogar_termos(current_usuario.id_cliente)
    await registrar_log(
        AcaoAuditoria.CONSENTIMENTO_REVOGADO, "FIDELIZACAO",
        usuario=current_usuario, id_entidade=current_usuario.id_cliente,
    )
    return resultado

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

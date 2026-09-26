from typing import Annotated
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import requer_cargo, requer_cliente_ou_cargo
from app.database import get_db_session
from app.domain.enums import AcaoAuditoria, CargoFunc
from app.models.cliente import Cliente
from app.models.funcionario import Funcionario
from app.domain.cargos import CARGOS_ADMIN, CARGOS_ATENDIMENTO
from app.schemas.cliente_schemas import ClienteRequest, ClienteResponse, ClienteUpdate
from app.services.auditoria_service import registrar_log
from app.services.cliente_service import ClienteService

router = APIRouter()

def get_cliente_service(db: Annotated[AsyncSession, Depends(get_db_session)]) -> ClienteService:
    return ClienteService(db)

@router.post("/", status_code=status.HTTP_201_CREATED, summary="Cadastrar cliente")
async def create_cliente(
    data: ClienteRequest,
    service: Annotated[ClienteService, Depends(get_cliente_service)],
) -> ClienteResponse:
    return await service.create_cliente(data)

@router.get("/{id_cliente}", summary="Buscar cliente por ID")
async def get_cliente_by_id(
    id_cliente: int,
    service: Annotated[ClienteService, Depends(get_cliente_service)],
    current_usuario: Annotated[Funcionario, Depends(
        requer_cargo(*CARGOS_ATENDIMENTO)
        )],
) -> ClienteResponse:
    return await service.get_cliente_by_id(id_cliente)

@router.get("/", summary="Listar clientes")
async def get_all_clientes(
    service: Annotated[ClienteService, Depends(get_cliente_service)],
    current_usuario: Annotated[Funcionario, Depends(
        requer_cargo(*CARGOS_ADMIN)
        )],
    offset: int = 0,
    limit: int = 10,
) -> list[ClienteResponse]:
    return await service.get_all_clientes(offset, limit)

@router.patch("/{id_cliente}", summary="Atualizar cliente")
async def update_cliente(
    id_cliente: int,
    data: ClienteUpdate,
    service: Annotated[ClienteService, Depends(get_cliente_service)],
    current_usuario: Annotated[Cliente | Funcionario, Depends(
        requer_cliente_ou_cargo(CargoFunc.ADMIN)
        )],
) -> ClienteResponse:
    cliente = await service.update_cliente(id_cliente, data)
    campos_alterados = list(data.model_dump(exclude_unset=True, exclude={"senha"}).keys())
    await registrar_log(
        AcaoAuditoria.ATUALIZACAO, "CLIENTE", usuario=current_usuario,
        id_entidade=id_cliente, detalhes={"campos_alterados": campos_alterados},
    )
    return cliente

@router.delete("/{id_cliente}", status_code=status.HTTP_204_NO_CONTENT, summary="Excluir cliente")
async def delete_cliente(
    id_cliente: int,
    service: Annotated[ClienteService, Depends(get_cliente_service)],
    current_usuario: Annotated[Cliente | Funcionario, Depends(
        requer_cliente_ou_cargo(CargoFunc.ADMIN)
        )],
):
    await service.delete_cliente(id_cliente)
    await registrar_log(
        AcaoAuditoria.EXCLUSAO, "CLIENTE", usuario=current_usuario, id_entidade=id_cliente,
    )

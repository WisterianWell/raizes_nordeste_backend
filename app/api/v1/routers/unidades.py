from typing import Annotated
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import requer_cargo, verificar_mesma_unidade
from app.database import get_db_session
from app.domain.enums import AcaoAuditoria, CargoFunc
from app.models.funcionario import Funcionario
from app.domain.cargos import CARGOS_ADMIN
from app.schemas.unidade_schemas import UnidadeRequest, UnidadeResponse, UnidadeUpdate
from app.services.auditoria_service import registrar_log
from app.services.unidade_service import UnidadeService

router = APIRouter()

def get_unidade_service(db: Annotated[AsyncSession, Depends(get_db_session)]) -> UnidadeService:
    return UnidadeService(db)

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_unidade(
    data: UnidadeRequest,
    service: Annotated[UnidadeService, Depends(get_unidade_service)],
    current_usuario: Annotated[Funcionario, Depends(
        requer_cargo(CargoFunc.ADMIN)
        )],
) -> UnidadeResponse:
    return await service.create_unidade(data)

@router.get("/{id_unidade}")
async def get_unidade_by_id(
    id_unidade: int,
    service: Annotated[UnidadeService, Depends(get_unidade_service)],
) -> UnidadeResponse:
    return await service.get_unidade_by_id(id_unidade)

@router.get("/")
async def get_all_unidades(
    service: Annotated[UnidadeService, Depends(get_unidade_service)],
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
    verificar_mesma_unidade(current_usuario, id_unidade)
    unidade = await service.update_unidade(id_unidade, data)
    campos_alterados = list(data.model_dump(exclude_unset=True).keys())
    await registrar_log(
        AcaoAuditoria.ATUALIZACAO, "UNIDADE", usuario=current_usuario,
        id_entidade=id_unidade, id_unidade=id_unidade,
        detalhes={"campos_alterados": campos_alterados},
    )
    return unidade

@router.delete("/{id_unidade}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_unidade(
    id_unidade: int,
    service: Annotated[UnidadeService, Depends(get_unidade_service)],
    current_usuario: Annotated[Funcionario, Depends(
        requer_cargo(CargoFunc.ADMIN)
        )],
):
    await service.delete_unidade(id_unidade)
    await registrar_log(
        AcaoAuditoria.EXCLUSAO, "UNIDADE", usuario=current_usuario,
        id_entidade=id_unidade, id_unidade=id_unidade,
    )

@router.post("/{id_unidade}/abrir")
async def abrir_unidade(
    id_unidade: int,
    service: Annotated[UnidadeService, Depends(get_unidade_service)],
    current_usuario: Annotated[Funcionario, Depends(
        requer_cargo(*CARGOS_ADMIN)
        )],
) -> UnidadeResponse:
    verificar_mesma_unidade(current_usuario, id_unidade)
    unidade = await service.abrir_unidade(id_unidade)
    await registrar_log(
        AcaoAuditoria.ABERTURA, "UNIDADE", usuario=current_usuario,
        id_entidade=id_unidade, id_unidade=id_unidade,
    )
    return unidade

@router.post("/{id_unidade}/fechar")
async def fechar_unidade(
    id_unidade: int,
    service: Annotated[UnidadeService, Depends(get_unidade_service)],
    current_usuario: Annotated[Funcionario, Depends(
        requer_cargo(*CARGOS_ADMIN)
        )],
) -> UnidadeResponse:
    verificar_mesma_unidade(current_usuario, id_unidade)
    unidade = await service.fechar_unidade(id_unidade)
    await registrar_log(
        AcaoAuditoria.FECHAMENTO, "UNIDADE", usuario=current_usuario,
        id_entidade=id_unidade, id_unidade=id_unidade,
    )
    return unidade

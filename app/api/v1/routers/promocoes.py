from typing import Annotated
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import requer_cargo
from app.database import get_db_session
from app.enums import AcaoAuditoria
from app.models.funcionario import Funcionario
from app.cargos import CARGOS_ADMIN
from app.schemas.promocao_schemas import PromocaoRequest, PromocaoResponse, PromocaoUpdate
from app.services.auditoria_service import registrar_log
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
    promocao = await service.create_promocao(data)
    await registrar_log(
        AcaoAuditoria.CRIACAO, "PROMOCAO", usuario=current_usuario,
        id_entidade=promocao.id_promocao, id_unidade=promocao.id_unidade,
    )
    return promocao

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
    promocao = await service.update_promocao(id_promocao, data)
    campos_alterados = list(data.model_dump(exclude_unset=True).keys())
    await registrar_log(
        AcaoAuditoria.ATUALIZACAO, "PROMOCAO", usuario=current_usuario,
        id_entidade=id_promocao, id_unidade=promocao.id_unidade,
        detalhes={"campos_alterados": campos_alterados},
    )
    return promocao

@router.delete("/{id_promocao}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_promocao(
    id_promocao: int,
    service: Annotated[PromocaoService, Depends(get_promocao_service)],
    current_usuario: Annotated[Funcionario, Depends(
        requer_cargo(*CARGOS_ADMIN)
        )],
):
    promocao = await service.get_promocao_by_id(id_promocao)
    await service.delete_promocao(id_promocao)
    await registrar_log(
        AcaoAuditoria.EXCLUSAO, "PROMOCAO", usuario=current_usuario,
        id_entidade=id_promocao, id_unidade=promocao.id_unidade,
    )

from typing import Annotated
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import requer_cargo
from app.database import get_db_session
from app.enums import AcaoAuditoria
from app.models.funcionario import Funcionario
from app.cargos import CARGOS_ADMIN
from app.schemas.funcionario_schemas import FuncionarioRequest, FuncionarioResponse, FuncionarioUpdate
from app.services.auditoria_service import registrar_log
from app.services.funcionario_service import FuncionarioService

router = APIRouter()

def get_funcionario_service(db: Annotated[AsyncSession, Depends(get_db_session)]) -> FuncionarioService:
    return FuncionarioService(db)

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_funcionario(
    data: FuncionarioRequest,
    service: Annotated[FuncionarioService, Depends(get_funcionario_service)],
    current_usuario: Annotated[Funcionario, Depends(
        requer_cargo(*CARGOS_ADMIN)
        )],
) -> FuncionarioResponse:
    funcionario = await service.create_funcionario(data)
    await registrar_log(
        AcaoAuditoria.CRIACAO, "FUNCIONARIO", usuario=current_usuario,
        id_entidade=funcionario.id_funcionario, id_unidade=funcionario.id_unidade,
        detalhes={"cargo": funcionario.cargo},
    )
    return funcionario

@router.get("/{id_funcionario}")
async def get_funcionario_by_id(
    id_funcionario: int,
    service: Annotated[FuncionarioService, Depends(get_funcionario_service)],
    current_usuario: Annotated[Funcionario, Depends(
        requer_cargo(*CARGOS_ADMIN)
        )],
) -> FuncionarioResponse:
    return await service.get_funcionario_by_id(id_funcionario)

@router.get("/")
async def get_funcionarios(
    service: Annotated[FuncionarioService, Depends(get_funcionario_service)],
    current_usuario: Annotated[Funcionario, Depends(
        requer_cargo(*CARGOS_ADMIN)
        )],
    id_unidade: int | None = None,
    offset: int = 0,
    limit: int = 10,
) -> list[FuncionarioResponse]:
    return await service.get_funcionarios(id_unidade, offset, limit)

@router.patch("/{id_funcionario}")
async def update_funcionario(
    id_funcionario: int,
    data: FuncionarioUpdate,
    service: Annotated[FuncionarioService, Depends(get_funcionario_service)],
    current_usuario: Annotated[Funcionario, Depends(
        requer_cargo(*CARGOS_ADMIN)
        )],
) -> FuncionarioResponse:
    funcionario = await service.update_funcionario(id_funcionario, data)
    campos_alterados = list(data.model_dump(exclude_unset=True, exclude={"senha"}).keys())
    await registrar_log(
        AcaoAuditoria.ATUALIZACAO, "FUNCIONARIO", usuario=current_usuario,
        id_entidade=id_funcionario, id_unidade=funcionario.id_unidade,
        detalhes={"campos_alterados": campos_alterados},
    )
    return funcionario

@router.delete("/{id_funcionario}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_funcionario(
    id_funcionario: int,
    service: Annotated[FuncionarioService, Depends(get_funcionario_service)],
    current_usuario: Annotated[Funcionario, Depends(
        requer_cargo(*CARGOS_ADMIN)
        )],
):
    funcionario = await service.get_funcionario_by_id(id_funcionario)
    await service.delete_funcionario(id_funcionario)
    await registrar_log(
        AcaoAuditoria.EXCLUSAO, "FUNCIONARIO", usuario=current_usuario,
        id_entidade=id_funcionario, id_unidade=funcionario.id_unidade,
    )

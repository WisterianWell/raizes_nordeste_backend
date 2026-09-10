from typing import Annotated
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import requer_cargo
from app.database import get_db_session
from app.models.funcionario import Funcionario
from app.repositories.enums import CargoFunc
from app.schemas.funcionario_schemas import FuncionarioRequest, FuncionarioResponse, FuncionarioUpdate
from app.services.funcionario_service import FuncionarioService

router = APIRouter()

def get_funcionario_service(db: Annotated[AsyncSession, Depends(get_db_session)]) -> FuncionarioService:
    return FuncionarioService(db)

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_funcionario(
    data: FuncionarioRequest,
    service: Annotated[FuncionarioService, Depends(get_funcionario_service)],
    current_usuario: Annotated[Funcionario, Depends(
        requer_cargo(CargoFunc.ADMIN, CargoFunc.GERENTE)
        )],
) -> FuncionarioResponse:
    return await service.create_funcionario(data)

@router.get("/{id_funcionario}")
async def get_funcionario_by_id(
    id_funcionario: int,
    service: Annotated[FuncionarioService, Depends(get_funcionario_service)],
    current_usuario: Annotated[Funcionario, Depends(
        requer_cargo(CargoFunc.ADMIN, CargoFunc.GERENTE)
        )],
) -> FuncionarioResponse:
    return await service.get_funcionario_by_id(id_funcionario)

@router.get("/")
async def get_all_funcionarios(
    service: Annotated[FuncionarioService, Depends(get_funcionario_service)],
    current_usuario: Annotated[Funcionario, Depends(
        requer_cargo(CargoFunc.ADMIN, CargoFunc.GERENTE)
        )],
    offset: int = 0,
    limit: int = 100,
) -> list[FuncionarioResponse]:
    return await service.get_all_funcionarios(offset, limit)

@router.patch("/{id_funcionario}")
async def update_funcionario(
    id_funcionario: int,
    data: FuncionarioUpdate,
    service: Annotated[FuncionarioService, Depends(get_funcionario_service)],
    current_usuario: Annotated[Funcionario, Depends(
        requer_cargo(CargoFunc.ADMIN, CargoFunc.GERENTE)
        )],
) -> FuncionarioResponse:
    return await service.update_funcionario(id_funcionario, data)

@router.delete("/{id_funcionario}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_funcionario(
    id_funcionario: int,
    service: Annotated[FuncionarioService, Depends(get_funcionario_service)],
    current_usuario: Annotated[Funcionario, Depends(
        requer_cargo(CargoFunc.ADMIN, CargoFunc.GERENTE)
        )],
):
    await service.delete_funcionario(id_funcionario)

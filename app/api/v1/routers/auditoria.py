from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import requer_cargo
from app.database import get_db_session
from app.models.funcionario import Funcionario
from app.domain.cargos import CARGOS_ADMIN
from app.schemas.auditoria_schemas import LogAuditoriaResponse
from app.services.auditoria_service import AuditoriaService

router = APIRouter()

def get_auditoria_service(db: Annotated[AsyncSession, Depends(get_db_session)]) -> AuditoriaService:
    return AuditoriaService(db)

@router.get("/", summary="Consultar logs de auditoria")
async def get_logs_auditoria(
    service: Annotated[AuditoriaService, Depends(get_auditoria_service)],
    current_usuario: Annotated[Funcionario, Depends(
        requer_cargo(*CARGOS_ADMIN)
        )],
    entidade: str | None = None,
    id_entidade: int | None = None,
    id_usuario: int | None = None,
    acao: str | None = None,
    id_unidade: int | None = None,
    offset: int = 0,
    limit: int = 10,
) -> list[LogAuditoriaResponse]:
    return await service.get_logs(entidade, id_entidade, id_usuario, acao, id_unidade, offset, limit)

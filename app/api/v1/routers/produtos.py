from typing import Annotated
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import requer_cargo
from app.database import get_db_session
from app.domain.enums import AcaoAuditoria, CargoFunc
from app.models.funcionario import Funcionario
from app.domain.cargos import CARGOS_ADMIN
from app.schemas.produto_schemas import ProdutoRequest, ProdutoResponse, ProdutoUpdate
from app.services.auditoria_service import registrar_log
from app.services.produto_service import ProdutoService

router = APIRouter()

def get_produto_service(db: Annotated[AsyncSession, Depends(get_db_session)]) -> ProdutoService:
    return ProdutoService(db)

@router.post("/", status_code=status.HTTP_201_CREATED, summary="Cadastrar produto")
async def create_produto(
    data: ProdutoRequest,
    service: Annotated[ProdutoService, Depends(get_produto_service)],
    current_usuario: Annotated[Funcionario, Depends(
        requer_cargo(CargoFunc.ADMIN)
        )],
) -> ProdutoResponse:
    produto = await service.create_produto(data)
    await registrar_log(
        AcaoAuditoria.CRIACAO, "PRODUTO", usuario=current_usuario, id_entidade=produto.id_produto,
    )
    return produto

@router.get("/{id_produto}", summary="Buscar produto por ID")
async def get_produto_by_id(
    id_produto: int,
    service: Annotated[ProdutoService, Depends(get_produto_service)],
    current_usuario: Annotated[Funcionario, Depends(
        requer_cargo(*CARGOS_ADMIN)
        )],
) -> ProdutoResponse:
    return await service.get_produto_by_id(id_produto)

@router.get("/", summary="Listar produtos")
async def get_produtos(
    service: Annotated[ProdutoService, Depends(get_produto_service)],
    current_usuario: Annotated[Funcionario, Depends(
        requer_cargo(*CARGOS_ADMIN)
        )],
    categoria: str | None = None,
    offset: int = 0,
    limit: int = 10,
) -> list[ProdutoResponse]:
    return await service.get_produtos(categoria, offset, limit)

@router.patch("/{id_produto}", summary="Atualizar produto")
async def update_produto(
    id_produto: int,
    data: ProdutoUpdate,
    service: Annotated[ProdutoService, Depends(get_produto_service)],
    current_usuario: Annotated[Funcionario, Depends(
        requer_cargo(CargoFunc.ADMIN)
        )],
) -> ProdutoResponse:
    produto = await service.update_produto(id_produto, data)
    campos_alterados = list(data.model_dump(exclude_unset=True).keys())
    await registrar_log(
        AcaoAuditoria.ATUALIZACAO, "PRODUTO", usuario=current_usuario,
        id_entidade=id_produto, detalhes={"campos_alterados": campos_alterados},
    )
    return produto

@router.delete("/{id_produto}", status_code=status.HTTP_204_NO_CONTENT, summary="Excluir produto")
async def delete_produto(
    id_produto: int,
    service: Annotated[ProdutoService, Depends(get_produto_service)],
    current_usuario: Annotated[Funcionario, Depends(
        requer_cargo(CargoFunc.ADMIN)
        )],
):
    await service.delete_produto(id_produto)
    await registrar_log(
        AcaoAuditoria.EXCLUSAO, "PRODUTO", usuario=current_usuario, id_entidade=id_produto,
    )

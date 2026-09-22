from datetime import datetime, timezone

from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.enums import TipoDesconto
from app.repositories.produto_repo import ProdutoRepository
from app.repositories.promocao_repo import PromocaoRepository
from app.repositories.unidade_repo import UnidadeRepository
from app.schemas.promocao_schemas import ItemPromocaoRequest, PromocaoRequest, PromocaoResponse, PromocaoUpdate
from app.exceptions import common_errors
from app.exceptions.error_codes import ErrorCodes
from app.exceptions.exceptions import AppException

class PromocaoService:
    def __init__(self, session: AsyncSession):
        self.repo = PromocaoRepository(session)
        self.produto_repo = ProdutoRepository(session)
        self.unidade_repo = UnidadeRepository(session)

    def _validate_data(self, data_inicio: datetime, data_fim: datetime) -> None:
        if data_fim <= data_inicio:
            raise AppException(
                status_code=status.HTTP_400_BAD_REQUEST,
                error_code=ErrorCodes.DATA_INVALIDA,
                message="data_fim deve ser posterior a data_inicio.",
                details=[{
                    "field": "data_fim",
                    "issue": "Data fim deve ser posterior a data_inicio"
                }],
            )

    async def _validate_unidade(self, id_unidade: int | None) -> None:
        if id_unidade is not None and not await self.unidade_repo.get_by_id(id_unidade):
            raise common_errors.unidade_nao_encontrada()

    async def _validate_itens(self, itens: list[ItemPromocaoRequest]) -> None:
        for index, item in enumerate(itens):
            if not await self.produto_repo.get_by_id(item.id_produto):
                raise AppException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    error_code=ErrorCodes.PRODUTO_NAO_ENCONTRADO,
                    message="Um ou mais produtos informados não foram encontrados.",
                    details=[{
                        "field": f"itens[{index}].id_produto",
                        "issue": f"Produto {item.id_produto} não encontrado",
                    }],
                )
            if item.tipo_valor == TipoDesconto.PERCENTUAL.value and not (0 < item.valor_desc <= 100):
                raise AppException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    error_code=ErrorCodes.DESCONTO_INVALIDO,
                    message="Um ou mais itens possuem valor de desconto inválido.",
                    details=[{
                        "field": f"itens[{index}].valor_desc",
                        "issue": "Para desconto percentual, deve estar entre 0 e 100",
                    }],
                )

    async def create_promocao(self, dados: PromocaoRequest) -> PromocaoResponse:
        self._validate_data(dados.data_inicio, dados.data_fim)
        await self._validate_unidade(dados.id_unidade)
        await self._validate_itens(dados.itens)
        promocao = await self.repo.create_promocao(
            itens=[item.model_dump() for item in dados.itens],
            id_unidade=dados.id_unidade,
            data_inicio=dados.data_inicio,
            data_fim=dados.data_fim,
        )
        return PromocaoResponse.model_validate(promocao)

    async def get_promocao_by_id(self, id_promocao: int) -> PromocaoResponse:
        promocao = await self.repo.get_by_id(id_promocao)
        if not promocao:
            raise common_errors.promocao_nao_encontrada()
        return PromocaoResponse.model_validate(promocao)

    async def get_promocoes(
        self,
        id_produto: int | None = None,
        id_unidade: int | None = None,
        ativo: bool | None = None,
        offset: int = 0,
        limit: int = 10,
    ) -> list[PromocaoResponse]:
        promocoes = await self.repo.get_promocoes(id_produto, id_unidade, ativo, offset, limit)
        return [PromocaoResponse.model_validate(p) for p in promocoes]

    async def update_promocao(self, id_promocao: int, dados: PromocaoUpdate) -> PromocaoResponse:
        promocao = await self.repo.get_by_id(id_promocao)
        if not promocao:
            raise common_errors.promocao_nao_encontrada()
        update_data = dados.model_dump(exclude_unset=True)
        data_inicio = update_data.get("data_inicio", promocao.data_inicio)
        data_fim = update_data.get("data_fim", promocao.data_fim)
        self._validate_data(data_inicio, data_fim)
        if "id_unidade" in update_data:
            await self._validate_unidade(update_data["id_unidade"])
        itens_data = None
        if "itens" in update_data:
            await self._validate_itens(dados.itens)
            itens_data = update_data.pop("itens")
        promocao = await self.repo.update_promocao(id_promocao, itens=itens_data, **update_data)
        return PromocaoResponse.model_validate(promocao)

    async def delete_promocao(self, id_promocao: int) -> None:
        deleted = await self.repo.delete(id_promocao)
        if not deleted:
            raise common_errors.promocao_nao_encontrada()

    async def calc_preco_desconto(self, id_produto: int, id_unidade: int, preco: float) -> float:
        date_now = datetime.now(timezone.utc)
        itens_vigentes = await self.repo.get_vigentes_by_item(id_produto, id_unidade, date_now)
        preco_desc = preco
        for item in itens_vigentes:
            if item.tipo_valor == TipoDesconto.PERCENTUAL.value:
                preco_com_desconto = preco * (1 - float(item.valor_desc) / 100)
            else:
                preco_com_desconto = preco - float(item.valor_desc)
            preco_desc = min(preco_desc, max(0.0, preco_com_desconto))
        return preco_desc

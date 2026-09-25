from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.enums import TipoMovEstoque
from app.models.item_cardapio import ItemCardapio
from app.models.item_estoque import ItemEstoque
from app.repositories.cardapio_repo import CardapioRepository
from app.repositories.estoque_repo import EstoqueRepository
from app.repositories.mov_estoque_repo import MovEstoqueRepository
from app.repositories.unidade_repo import UnidadeRepository
from app.schemas.cardapio_schemas import CardapioResponse
from app.schemas.mov_estoque_schemas import MovEstoqueRequest, MovEstoqueResponse
from app.exceptions import common_errors
from app.exceptions.error_codes import ErrorCodes
from app.exceptions.exceptions import AppException
from app.services.promocao_service import PromocaoService

class EstoqueService:
    def __init__(self, session: AsyncSession):
        self.repo = EstoqueRepository(session)
        self.cardapio_repo = CardapioRepository(session)
        self.mov_estoque_repo = MovEstoqueRepository(session)
        self.unidade_repo = UnidadeRepository(session)
        self.promocao_service = PromocaoService(session)

    async def _build_response(self, item_cardapio: ItemCardapio, estoque: ItemEstoque) -> CardapioResponse:
        preco = float(item_cardapio.preco)
        preco_com_desconto = await self.promocao_service.calc_preco_desconto(
            item_cardapio.id_produto, item_cardapio.id_unidade, preco
        )
        return CardapioResponse(
            id_produto=item_cardapio.id_produto,
            id_unidade=item_cardapio.id_unidade,
            nome=item_cardapio.nome,
            categoria=item_cardapio.categoria,
            preco=preco,
            preco_promo=round(preco_com_desconto, 2) if preco_com_desconto < preco else None,
            estoque=estoque.quantidade,
            ativo=item_cardapio.ativo,
        )

    async def _search_item(self, id_produto: int, id_unidade: int) -> tuple[ItemCardapio, ItemEstoque]:
        item_cardapio = await self.cardapio_repo.get_item_cardapio(id_produto, id_unidade)
        estoque = await self.repo.get_item_estoque(id_produto, id_unidade)
        if not item_cardapio or not estoque:
            raise common_errors.item_cardapio_nao_encontrado()
        return item_cardapio, estoque

    async def get_estoque_by_unidade(
        self, id_unidade: int, offset: int = 0, limit: int = 10
    ) -> list[CardapioResponse]:
        itens = await self.cardapio_repo.get_itens_by_unidade(id_unidade, offset, limit, apenas_disponiveis=False)
        estoques = {e.id_produto: e for e in await self.repo.get_by_unidade(id_unidade)}
        return [
            await self._build_response(item, estoques[item.id_produto])
            for item in itens
            if item.id_produto in estoques
        ]

    async def criar_entrada(self, dados: MovEstoqueRequest) -> list[MovEstoqueResponse]:
        resultados = []
        for item in dados.itens:
            _, estoque_atual = await self._search_item(item.id_produto, item.id_unidade)
            await self.repo.update_item_estoque(
                item.id_produto, item.id_unidade, quantidade=estoque_atual.quantidade + item.quantidade
            )
            movimentacao = await self.mov_estoque_repo.create(
                id_produto=item.id_produto,
                id_unidade=item.id_unidade,
                tipo=TipoMovEstoque.ENTRADA.value,
                quantidade=item.quantidade,
            )
            resultados.append(MovEstoqueResponse.model_validate(movimentacao))
        return resultados

    async def criar_saida(self, dados: MovEstoqueRequest) -> list[MovEstoqueResponse]:
        resultados = []
        for index, item in enumerate(dados.itens):
            _, estoque_atual = await self._search_item(item.id_produto, item.id_unidade)
            if item.quantidade > estoque_atual.quantidade:
                raise AppException(
                    status_code=status.HTTP_409_CONFLICT,
                    error_code=ErrorCodes.ESTOQUE_INSUFICIENTE,
                    message="Não há quantidade suficiente para um ou mais itens.",
                    details=[{
                        "field": f"itens[{index}].quantidade",
                        "issue": f"Quantidade disponível: {estoque_atual.quantidade}",
                    }],
                )
            await self.repo.update_item_estoque(
                item.id_produto, item.id_unidade, quantidade=estoque_atual.quantidade - item.quantidade
            )
            movimentacao = await self.mov_estoque_repo.create(
                id_produto=item.id_produto,
                id_unidade=item.id_unidade,
                tipo=TipoMovEstoque.SAIDA.value,
                quantidade=-item.quantidade,
            )
            resultados.append(MovEstoqueResponse.model_validate(movimentacao))
        return resultados

    async def get_movimentacoes(
        self, id_unidade: int, id_produto: int | None = None, offset: int = 0, limit: int = 10
    ) -> list[MovEstoqueResponse]:
        if id_produto is not None:
            if not await self.repo.get_item_estoque(id_produto, id_unidade):
                raise common_errors.item_cardapio_nao_encontrado()
        elif not await self.unidade_repo.get_by_id(id_unidade):
            raise common_errors.unidade_nao_encontrada()
        movimentacoes = await self.mov_estoque_repo.get_by_unidade(id_unidade, id_produto, offset, limit)
        return [MovEstoqueResponse.model_validate(m) for m in movimentacoes]

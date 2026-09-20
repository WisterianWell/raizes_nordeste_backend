from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.item_estoque import ItemEstoque
from app.models.item_cardapio import ItemCardapio
from app.repositories.cardapio_repo import CardapioRepository
from app.repositories.estoque_repo import EstoqueRepository
from app.repositories.produto_repo import ProdutoRepository
from app.repositories.unidade_repo import UnidadeRepository
from app.schemas.cardapio_schemas import (
    CardapioPublicoResponse,
    CardapioRequest,
    CardapioResponse,
    CardapioUpdate,
)
from app.services.promocao_service import PromocaoService

class CardapioService:
    def __init__(self, session: AsyncSession):
        self.repo = CardapioRepository(session)
        self.estoque_repo = EstoqueRepository(session)
        self.produto_repo = ProdutoRepository(session)
        self.unidade_repo = UnidadeRepository(session)
        self.promocao_service = PromocaoService(session)

    async def _calc_preco_promo(self, item_cardapio: ItemCardapio, preco: float) -> float | None:
        preco_com_desconto = await self.promocao_service.calc_preco_desconto(
            item_cardapio.id_produto, item_cardapio.id_unidade, preco
        )
        return preco_com_desconto if preco_com_desconto < preco else None

    async def _build_response(self, item_cardapio: ItemCardapio, estoque: ItemEstoque) -> CardapioResponse:
        preco = float(item_cardapio.preco)
        return CardapioResponse(
            id_produto=item_cardapio.id_produto,
            id_unidade=item_cardapio.id_unidade,
            nome=item_cardapio.nome,
            categoria=item_cardapio.categoria,
            preco=preco,
            preco_promo=await self._calc_preco_promo(item_cardapio, preco),
            estoque=estoque.quantidade,
            disponivel=item_cardapio.disponivel,
        )

    async def _build_publico_response(self, item_cardapio: ItemCardapio) -> CardapioPublicoResponse:
        preco = float(item_cardapio.preco)
        return CardapioPublicoResponse(
            id_produto=item_cardapio.id_produto,
            id_unidade=item_cardapio.id_unidade,
            nome=item_cardapio.nome,
            categoria=item_cardapio.categoria,
            preco=preco,
            preco_promo=await self._calc_preco_promo(item_cardapio, preco),
            disponivel=item_cardapio.disponivel,
        )

    async def create_cardapio(self, dados: CardapioRequest) -> CardapioResponse:
        if not await self.produto_repo.get_by_id(dados.id_produto):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Produto não encontrado."
            )
        if not await self.unidade_repo.get_by_id(dados.id_unidade):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Unidade não encontrada."
            )
        if await self.repo.get_item_cardapio(dados.id_produto, dados.id_unidade):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Produto já cadastrado nessa unidade."
            )
        item_cardapio = await self.repo.create_item_cardapio(
            id_produto=dados.id_produto,
            id_unidade=dados.id_unidade,
            preco=dados.preco,
            disponivel=dados.disponivel,
        )
        estoque = await self.estoque_repo.create_item_estoque(
            id_produto=dados.id_produto,
            id_unidade=dados.id_unidade,
            quantidade=dados.estoque,
        )
        return await self._build_response(item_cardapio, estoque)

    async def get_item(self, id_produto: int, id_unidade: int) -> CardapioResponse:
        item_cardapio = await self.repo.get_item_cardapio(id_produto, id_unidade)
        estoque = await self.estoque_repo.get_item_estoque(id_produto, id_unidade)
        if not item_cardapio or not estoque:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Produto não encontrado nessa unidade."
            )
        return await self._build_response(item_cardapio, estoque)

    async def get_cardapio_by_unidade(
        self, id_unidade: int, offset: int = 0, limit: int = 10, apenas_disponiveis: bool = False
    ) -> list[CardapioPublicoResponse]:
        itens = await self.repo.get_itens_by_unidade(id_unidade, offset, limit, apenas_disponiveis)
        return [await self._build_publico_response(item) for item in itens]

    async def update_item(
        self, id_produto: int, id_unidade: int, dados: CardapioUpdate
    ) -> CardapioResponse:
        item_cardapio = await self.repo.get_item_cardapio(id_produto, id_unidade)
        estoque = await self.estoque_repo.get_item_estoque(id_produto, id_unidade)
        if not item_cardapio or not estoque:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Produto não encontrado nessa unidade."
            )
        update_data = dados.model_dump(exclude_unset=True)
        item_cardapio = await self.repo.update_item_cardapio(id_produto, id_unidade, **update_data)
        return await self._build_response(item_cardapio, estoque)

    async def delete_item(self, id_produto: int, id_unidade: int) -> None:
        deleted = await self.repo.delete_item_cardapio(id_produto, id_unidade)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Produto não encontrado nessa unidade."
            )
        await self.estoque_repo.delete_item_estoque(id_produto, id_unidade)

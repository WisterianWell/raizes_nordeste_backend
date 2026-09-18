from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cardapio import Cardapio
from app.models.estoque import Estoque
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

class CardapioService:
    def __init__(self, session: AsyncSession):
        self.repo = CardapioRepository(session)
        self.estoque_repo = EstoqueRepository(session)
        self.produto_repo = ProdutoRepository(session)
        self.unidade_repo = UnidadeRepository(session)

    def _build_response(self, cardapio: Cardapio, estoque: Estoque) -> CardapioResponse:
        return CardapioResponse(
            id_produto=cardapio.id_produto,
            id_unidade=cardapio.id_unidade,
            nome=cardapio.nome,
            categoria=cardapio.categoria,
            preco=float(cardapio.preco),
            estoque=estoque.quantidade,
            disponivel=cardapio.disponivel,
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
        cardapio = await self.repo.create_item_cardapio(
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
        return self._build_response(cardapio, estoque)

    async def get_item(self, id_produto: int, id_unidade: int) -> CardapioResponse:
        cardapio = await self.repo.get_item_cardapio(id_produto, id_unidade)
        estoque = await self.estoque_repo.get_item_estoque(id_produto, id_unidade)
        if not cardapio or not estoque:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Produto não encontrado nessa unidade."
            )
        return self._build_response(cardapio, estoque)

    async def get_cardapio_by_unidade(
        self, id_unidade: int, offset: int = 0, limit: int = 10, apenas_disponiveis: bool = False
    ) -> list[CardapioPublicoResponse]:
        itens = await self.repo.get_itens_by_unidade(id_unidade, offset, limit, apenas_disponiveis)
        return [CardapioPublicoResponse.model_validate(item) for item in itens]

    async def update_item(
        self, id_produto: int, id_unidade: int, dados: CardapioUpdate
    ) -> CardapioResponse:
        cardapio = await self.repo.get_item_cardapio(id_produto, id_unidade)
        estoque = await self.estoque_repo.get_item_estoque(id_produto, id_unidade)
        if not cardapio or not estoque:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Produto não encontrado nessa unidade."
            )
        update_data = dados.model_dump(exclude_unset=True)
        cardapio = await self.repo.update_item_cardapio(id_produto, id_unidade, **update_data)
        return self._build_response(cardapio, estoque)

    async def delete_item(self, id_produto: int, id_unidade: int) -> None:
        deleted = await self.repo.delete_item_cardapio(id_produto, id_unidade)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Produto não encontrado nessa unidade."
            )
        await self.estoque_repo.delete_item_estoque(id_produto, id_unidade)

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.enums import TipoMovimentacao
from app.models.cardapio import Cardapio
from app.models.estoque import Estoque
from app.repositories.cardapio_repo import CardapioRepository
from app.repositories.estoque_repo import EstoqueRepository
from app.repositories.mov_estoque_repo import MovEstoqueRepository
from app.repositories.unidade_repo import UnidadeRepository
from app.schemas.cardapio_schemas import CardapioResponse
from app.schemas.mov_estoque_schemas import MovEstoqueRequest, MovEstoqueResponse

class EstoqueService:
    def __init__(self, session: AsyncSession):
        self.repo = EstoqueRepository(session)
        self.cardapio_repo = CardapioRepository(session)
        self.mov_estoque_repo = MovEstoqueRepository(session)
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
    
    async def _search_item(self, id_produto: int, id_unidade: int) -> tuple[Cardapio, Estoque]:
        cardapio = await self.cardapio_repo.get_item_cardapio(id_produto, id_unidade)
        estoque = await self.repo.get_item_estoque(id_produto, id_unidade)
        if not cardapio or not estoque:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Produto não encontrado nessa unidade."
            )
        return cardapio, estoque

    async def get_estoque_by_unidade(
        self, id_unidade: int, offset: int = 0, limit: int = 10
    ) -> list[CardapioResponse]:
        itens = await self.cardapio_repo.get_itens_by_unidade(id_unidade, offset, limit, apenas_disponiveis=False)
        estoques = {e.id_produto: e for e in await self.repo.get_by_unidade(id_unidade)}
        return [
            self._build_response(item, estoques[item.id_produto])
            for item in itens
            if item.id_produto in estoques
        ]

    async def dar_entrada(
        self, id_produto: int, id_unidade: int, dados: MovEstoqueRequest
    ) -> MovEstoqueResponse:
        _, estoque_atual = await self._search_item(id_produto, id_unidade)
        await self.repo.update_item_estoque(
            id_produto, id_unidade, quantidade=estoque_atual.quantidade + dados.quantidade
        )
        movimentacao = await self.mov_estoque_repo.create(
            id_produto=id_produto,
            id_unidade=id_unidade,
            tipo=TipoMovimentacao.ENTRADA.value,
            quantidade=dados.quantidade,
        )
        return MovEstoqueResponse.model_validate(movimentacao)

    async def dar_saida(
        self, id_produto: int, id_unidade: int, dados: MovEstoqueRequest
    ) -> MovEstoqueResponse:
        _, estoque_atual = await self._search_item(id_produto, id_unidade)
        if dados.quantidade > estoque_atual.quantidade:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Estoque insuficiente para essa saída."
            )
        await self.repo.update_item_estoque(
            id_produto, id_unidade, quantidade=estoque_atual.quantidade - dados.quantidade
        )
        movimentacao = await self.mov_estoque_repo.create(
            id_produto=id_produto,
            id_unidade=id_unidade,
            tipo=TipoMovimentacao.SAIDA.value,
            quantidade=-dados.quantidade,
        )
        return MovEstoqueResponse.model_validate(movimentacao)

    async def get_movimentacoes(
        self, id_unidade: int, id_produto: int | None = None, offset: int = 0, limit: int = 10
    ) -> list[MovEstoqueResponse]:
        if id_produto is not None:
            if not await self.repo.get_item_estoque(id_produto, id_unidade):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Produto não encontrado nessa unidade."
                )
        elif not await self.unidade_repo.get_by_id(id_unidade):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Unidade não encontrada."
            )
        movimentacoes = await self.mov_estoque_repo.get_by_unidade(id_unidade, id_produto, offset, limit)
        return [MovEstoqueResponse.model_validate(m) for m in movimentacoes]

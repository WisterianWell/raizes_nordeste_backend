from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.cardapio_repo import CardapioRepository
from app.repositories.produto_repo import ProdutoRepository
from app.repositories.unidade_repo import UnidadeRepository
from app.schemas.cardapio_schemas import CardapioRequest, CardapioResponse, CardapioUpdate

class CardapioService:
    def __init__(self, session: AsyncSession):
        self.repo = CardapioRepository(session)
        self.produto_repo = ProdutoRepository(session)
        self.unidade_repo = UnidadeRepository(session)

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
        novo = await self.repo.create_item_cardapio(
            id_produto=dados.id_produto,
            id_unidade=dados.id_unidade,
            preco=dados.preco,
            estoque=dados.estoque,
            disponivel=dados.disponivel,
        )
        return CardapioResponse.model_validate(novo)

    async def get_item(self, id_produto: int, id_unidade: int) -> CardapioResponse:
        item = await self.repo.get_item_cardapio(id_produto, id_unidade)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Produto não encontrado nessa unidade."
            )
        return CardapioResponse.model_validate(item)

    async def get_cardapio_by_unidade(
        self, id_unidade: int, offset: int = 0, limit: int = 100, apenas_disponiveis: bool = False
    ) -> list[CardapioResponse]:
        itens = await self.repo.get_itens_by_unidade(id_unidade, offset, limit, apenas_disponiveis)
        return [CardapioResponse.model_validate(item) for item in itens]

    async def update_item(
        self, id_produto: int, id_unidade: int, dados: CardapioUpdate
    ) -> CardapioResponse:
        if not await self.repo.get_item_cardapio(id_produto, id_unidade):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Produto não encontrado nessa unidade."
            )
        update_data = dados.model_dump(exclude_unset=True)
        item = await self.repo.update_item_cardapio(id_produto, id_unidade, **update_data)
        return CardapioResponse.model_validate(item)

    async def delete_item(self, id_produto: int, id_unidade: int) -> None:
        deleted = await self.repo.delete_item_cardapio(id_produto, id_unidade)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Produto não encontrado nessa unidade."
            )

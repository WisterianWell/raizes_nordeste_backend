from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.produto_repo import ProdutoRepository
from app.schemas.produto_schemas import ProdutoRequest, ProdutoResponse, ProdutoUpdate

class ProdutoService:
    def __init__(self, session: AsyncSession):
        self.repo = ProdutoRepository(session)

    async def create_produto(self, produto: ProdutoRequest) -> ProdutoResponse:
        novo_produto = await self.repo.create(
            nome=produto.nome,
            categoria=produto.categoria,
        )
        return ProdutoResponse.model_validate(novo_produto)

    async def get_produto_by_id(self, id_produto: int) -> ProdutoResponse:
        produto = await self.repo.get_by_id(id_produto)
        if not produto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Produto não encontrado."
            )
        return ProdutoResponse.model_validate(produto)

    async def get_produtos(
        self, categoria: str | None = None, offset: int = 0, limit: int = 10
    ) -> list[ProdutoResponse]:
        produtos = await self.repo.get_produtos(categoria, offset, limit)
        return [ProdutoResponse.model_validate(produto) for produto in produtos]

    async def update_produto(self, id_produto: int, dados: ProdutoUpdate) -> ProdutoResponse:
        produto = await self.repo.get_by_id(id_produto)
        if not produto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Produto não encontrado."
            )
        update_data = dados.model_dump(exclude_unset=True)
        produto = await self.repo.update(id_produto, **update_data)
        return ProdutoResponse.model_validate(produto)

    async def delete_produto(self, id_produto: int) -> None:
        deleted = await self.repo.delete(id_produto)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Produto não encontrado."
            )

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.produto import Produto
from app.repositories.base import BaseRepository

class ProdutoRepository(BaseRepository[Produto]):
    def __init__(self, session: AsyncSession):
        super().__init__(Produto, session)

    async def get_by_id(self, id: int) -> Produto | None:
        query = select(Produto).where(Produto.id_produto == id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_all_produtos(self, offset: int = 0, limit: int = 100) -> list[Produto]:
        query = (
            select(Produto)
            .offset(offset)
            .limit(limit)
            .order_by(Produto.created_at.desc())
            )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_categoria(self, categoria: str, offset: int = 0, limit: int = 100) -> list[Produto]:
        query = (
            select(Produto)
            .where(Produto.categoria == categoria)
            .offset(offset)
            .limit(limit)
            .order_by(Produto.created_at.desc())
            )
        result = await self.session.execute(query)
        return list(result.scalars().all())

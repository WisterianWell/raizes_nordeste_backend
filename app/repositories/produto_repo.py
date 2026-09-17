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

    async def get_produtos(
        self, categoria: str | None = None, offset: int = 0, limit: int = 100
    ) -> list[Produto]:
        query = select(Produto)
        if categoria is not None:
            query = query.where(Produto.categoria == categoria)
        query = query.offset(offset).limit(limit).order_by(Produto.created_at.desc())
        result = await self.session.execute(query)
        return list(result.scalars().all())

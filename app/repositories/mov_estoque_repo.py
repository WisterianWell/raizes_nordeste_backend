from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.mov_estoque import MovEstoque
from app.repositories.base import BaseRepository

class MovEstoqueRepository(BaseRepository[MovEstoque]):
    def __init__(self, session: AsyncSession):
        super().__init__(MovEstoque, session)

    async def get_by_unidade(
        self, id_unidade: int, id_produto: int | None = None, offset: int = 0, limit: int = 10
    ) -> list[MovEstoque]:
        query = select(MovEstoque).where(MovEstoque.id_unidade == id_unidade)
        if id_produto is not None:
            query = query.where(MovEstoque.id_produto == id_produto)
        query = query.offset(offset).limit(limit).order_by(MovEstoque.created_at.desc())
        result = await self.session.execute(query)
        return list(result.scalars().all())

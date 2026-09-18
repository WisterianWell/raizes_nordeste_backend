from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.estoque import Estoque
from app.repositories.base import BaseRepository

class EstoqueRepository(BaseRepository[Estoque]):
    def __init__(self, session: AsyncSession):
        super().__init__(Estoque, session)

    async def get_item_estoque(self, id_produto: int, id_unidade: int) -> Estoque | None:
        return await self.get_by_id(id_produto, id_unidade)

    async def get_by_unidade(self, id_unidade: int) -> list[Estoque]:
        query = select(Estoque).where(Estoque.id_unidade == id_unidade)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def create_item_estoque(self, **kwargs) -> Estoque:
        return await self.create(**kwargs)

    async def update_item_estoque(self, id_produto: int, id_unidade: int, **kwargs) -> Estoque | None:
        return await self.update(id_produto, id_unidade, **kwargs)

    async def delete_item_estoque(self, id_produto: int, id_unidade: int) -> bool:
        return await self.delete(id_produto, id_unidade)

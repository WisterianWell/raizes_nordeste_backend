from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.item_cardapio import ItemCardapio
from app.repositories.base import BaseRepository

class CardapioRepository(BaseRepository[ItemCardapio]):
    def __init__(self, session: AsyncSession):
        super().__init__(ItemCardapio, session)

    async def create_item_cardapio(self, **kwargs) -> ItemCardapio:
        instance = await self.create(**kwargs)
        return await self.get_item_cardapio(instance.id_produto, instance.id_unidade)

    async def get_item_cardapio(self, id_produto: int, id_unidade: int) -> ItemCardapio | None:
        return await self.get_by_id(id_produto, id_unidade)

    async def get_itens_by_unidade(
        self, id_unidade: int, offset: int = 0, limit: int = 10, apenas_disponiveis: bool = False
    ) -> list[ItemCardapio]:
        query = select(ItemCardapio).where(ItemCardapio.id_unidade == id_unidade)
        if apenas_disponiveis:
            query = query.where(ItemCardapio.ativo.is_(True))
        query = query.offset(offset).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update_item_cardapio(self, id_produto: int, id_unidade: int, **kwargs) -> ItemCardapio | None:
        instance = await self.update(id_produto, id_unidade, **kwargs)
        if not instance:
            return None
        return await self.get_item_cardapio(id_produto, id_unidade)

    async def delete_item_cardapio(self, id_produto: int, id_unidade: int) -> bool:
        return await self.delete(id_produto, id_unidade)

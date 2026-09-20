from datetime import datetime

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.item_promocao import ItemPromocao
from app.models.promocao import Promocao
from app.repositories.base import BaseRepository

class PromocaoRepository(BaseRepository[Promocao]):
    def __init__(self, session: AsyncSession):
        super().__init__(Promocao, session)

    async def get_by_id(self, id_promocao: int) -> Promocao | None:
        query = (
            select(Promocao)
            .where(Promocao.id_promocao == id_promocao)
            .options(selectinload(Promocao.itens).selectinload(ItemPromocao.produto))
            .execution_options(populate_existing=True)
            )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create_promocao(self, itens: list[dict], **kwargs) -> Promocao:
        instance = Promocao(itens=[ItemPromocao(**item) for item in itens], **kwargs)
        self.session.add(instance)
        await self.session.flush()
        return await self.get_by_id(instance.id_promocao)

    async def update_promocao(
        self, id_promocao: int, itens: list[dict] | None = None, **kwargs
    ) -> Promocao | None:
        instance = await self.get_by_id(id_promocao)
        if not instance:
            return None
        for key, value in kwargs.items():
            setattr(instance, key, value)
        if itens is not None:
            instance.itens = [ItemPromocao(**item) for item in itens]
        await self.session.flush()
        return await self.get_by_id(id_promocao)

    async def get_promocoes(
        self,
        id_produto: int | None = None,
        id_unidade: int | None = None,
        ativo: bool | None = None,
        offset: int = 0,
        limit: int = 10,
    ) -> list[Promocao]:
        query = select(Promocao).options(selectinload(Promocao.itens).selectinload(ItemPromocao.produto))
        if id_produto is not None:
            query = query.where(Promocao.itens.any(ItemPromocao.id_produto == id_produto))
        if id_unidade is not None:
            query = query.where(Promocao.id_unidade == id_unidade)
        if ativo is not None:
            query = query.where(Promocao.ativo.is_(ativo))
        query = query.offset(offset).limit(limit).order_by(Promocao.created_at.desc())
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_vigentes_by_item(self, id_produto: int, id_unidade: int, date_now: datetime) -> list[ItemPromocao]:
        query = (
            select(ItemPromocao)
            .join(Promocao, ItemPromocao.id_promocao == Promocao.id_promocao)
            .where(
                ItemPromocao.id_produto == id_produto,
                Promocao.ativo.is_(True),
                Promocao.data_inicio <= date_now,
                Promocao.data_fim >= date_now,
                or_(Promocao.id_unidade.is_(None), Promocao.id_unidade == id_unidade),
            )
            )
        result = await self.session.execute(query)
        return list(result.scalars().all())

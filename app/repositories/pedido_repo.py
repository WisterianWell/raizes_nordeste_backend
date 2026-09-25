from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.item_pedido import ItemPedido
from app.models.pedido import Pedido
from app.repositories.base import BaseRepository

class PedidoRepository(BaseRepository[Pedido]):
    def __init__(self, session: AsyncSession):
        super().__init__(Pedido, session)

    async def get_by_id(self, id_pedido: int) -> Pedido | None:
        query = (
            select(Pedido)
            .where(Pedido.id_pedido == id_pedido)
            .options(
                selectinload(Pedido.itens).selectinload(ItemPedido.produto),
                selectinload(Pedido.pagamentos),
                )
            .execution_options(populate_existing=True)
            )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create_pedido(self, itens: list[dict], **kwargs) -> Pedido:
        instance = Pedido(itens=[ItemPedido(**item) for item in itens], **kwargs)
        self.session.add(instance)
        await self.session.flush()
        return await self.get_by_id(instance.id_pedido)

    async def get_pedidos(
        self,
        id_cliente: int | None = None,
        id_unidade: int | None = None,
        canal: str | None = None,
        offset: int = 0,
        limit: int = 10,
    ) -> list[Pedido]:
        query = select(Pedido)
        if id_cliente is not None:
            query = query.where(Pedido.id_cliente == id_cliente)
        if id_unidade is not None:
            query = query.where(Pedido.id_unidade == id_unidade)
        if canal is not None:
            query = query.where(Pedido.canal == canal)
        query = query.offset(offset).limit(limit).order_by(Pedido.created_at.desc())
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update_status_pedido(self, id_pedido: int, status_pedido: str) -> Pedido | None:
        atualizado = await self.update(id_pedido, status_pedido=status_pedido)
        if not atualizado:
            return None
        return await self.get_by_id(id_pedido)

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.enums import TipoMovPontos
from app.models.mov_pontos import MovPontos
from app.repositories.base import BaseRepository

class MovPontosRepository(BaseRepository[MovPontos]):
    def __init__(self, session: AsyncSession):
        super().__init__(MovPontos, session)

    async def get_by_cliente(self, id_cliente: int, offset: int = 0, limit: int = 10) -> list[MovPontos]:
        query = (
            select(MovPontos)
            .where(MovPontos.id_cliente == id_cliente)
            .offset(offset)
            .limit(limit)
            .order_by(MovPontos.created_at.desc())
            )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_ganho_by_pedido(self, id_cliente: int, id_pedido: int) -> MovPontos | None:
        query = select(MovPontos).where(
            MovPontos.id_cliente == id_cliente,
            MovPontos.id_pedido == id_pedido,
            MovPontos.tipo == TipoMovPontos.GANHO.value,
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_resgate_by_pedido(self, id_cliente: int, id_pedido: int) -> MovPontos | None:
        query = select(MovPontos).where(
            MovPontos.id_cliente == id_cliente,
            MovPontos.id_pedido == id_pedido,
            MovPontos.tipo == TipoMovPontos.RESGATE.value,
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

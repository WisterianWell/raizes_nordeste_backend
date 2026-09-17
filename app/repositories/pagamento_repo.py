from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.pagamento import Pagamento
from app.repositories.base import BaseRepository

class PagamentoRepository(BaseRepository[Pagamento]):
    def __init__(self, session: AsyncSession):
        super().__init__(Pagamento, session)

    async def get_by_pedido(self, id_pedido: int, offset: int = 0, limit: int = 10) -> list[Pagamento]:
        query = (
            select(Pagamento)
            .where(Pagamento.id_pedido == id_pedido)
            .offset(offset)
            .limit(limit)
            .order_by(Pagamento.created_at.desc())
            )
        result = await self.session.execute(query)
        return list(result.scalars().all())

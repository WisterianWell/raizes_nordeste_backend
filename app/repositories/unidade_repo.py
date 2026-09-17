from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.unidade import Unidade
from app.repositories.base import BaseRepository

class UnidadeRepository(BaseRepository[Unidade]):
    def __init__(self, session: AsyncSession):
        super().__init__(Unidade, session)

    async def get_by_id(self, id: int) -> Unidade | None:
        query = select(Unidade).where(Unidade.id_unidade == id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_all_unidades(self, offset: int = 0, limit: int = 10) -> list[Unidade]:
        query = (
            select(Unidade)
            .offset(offset)
            .limit(limit)
            .order_by(Unidade.created_at.desc())
            )
        result = await self.session.execute(query)
        return list(result.scalars().all())

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cliente import Cliente
from app.repositories.base import BaseRepository

class ClienteRepository(BaseRepository[Cliente]):
    def __init__(self, session: AsyncSession):
        super().__init__(Cliente, session)

    async def get_by_id(self, id: int) -> Cliente | None:
        query = select(Cliente).where(Cliente.id_cliente == id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Cliente | None:
        query = select(Cliente).where(Cliente.email == email)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_cpf(self, cpf: str) -> Cliente | None:
        query = select(Cliente).where(Cliente.cpf == cpf)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_all_clientes(self, offset: int = 0, limit: int = 100) -> list[Cliente]:
        query = (
            select(Cliente)
            .offset(offset)
            .limit(limit)
            .order_by(Cliente.created_at.desc())
            )
        result = await self.session.execute(query)
        return list(result.scalars().all())
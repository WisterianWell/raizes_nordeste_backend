from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.funcionario import Funcionario
from app.repositories.base import BaseRepository

class FuncionarioRepository(BaseRepository[Funcionario]):
    def __init__(self, session: AsyncSession):
        super().__init__(Funcionario, session)

    async def get_by_id(self, id: int) -> Funcionario | None:
        query = select(Funcionario).where(Funcionario.id_funcionario == id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Funcionario | None:
        query = select(Funcionario).where(Funcionario.email == email)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_cpf(self, cpf: str) -> Funcionario | None:
        query = select(Funcionario).where(Funcionario.cpf == cpf)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_all_funcionarios(self, offset: int = 0, limit: int = 100) -> list[Funcionario]:
        query = (
            select(Funcionario)
            .offset(offset)
            .limit(limit)
            .order_by(Funcionario.created_at.desc())
            )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_unidade(self, id_unidade: int, offset: int = 0, limit: int = 100) -> list[Funcionario]:
        query = (
            select(Funcionario)
            .where(Funcionario.id_unidade == id_unidade)
            .offset(offset)
            .limit(limit)
            .order_by(Funcionario.created_at.desc())
            )
        result = await self.session.execute(query)
        return list(result.scalars().all())

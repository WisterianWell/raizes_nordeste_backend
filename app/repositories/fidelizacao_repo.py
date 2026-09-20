from sqlalchemy.ext.asyncio import AsyncSession

from app.models.fidelizacao import Fidelizacao
from app.repositories.base import BaseRepository

class FidelizacaoRepository(BaseRepository[Fidelizacao]):
    def __init__(self, session: AsyncSession):
        super().__init__(Fidelizacao, session)

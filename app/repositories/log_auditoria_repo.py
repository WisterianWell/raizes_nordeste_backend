from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.log_auditoria import LogAuditoria
from app.repositories.base import BaseRepository

class LogAuditoriaRepository(BaseRepository[LogAuditoria]):
    def __init__(self, session: AsyncSession):
        super().__init__(LogAuditoria, session)

    async def get_logs(
        self,
        entidade: str | None = None,
        id_entidade: int | None = None,
        id_usuario: int | None = None,
        acao: str | None = None,
        id_unidade: int | None = None,
        offset: int = 0,
        limit: int = 10,
    ) -> list[LogAuditoria]:
        query = select(LogAuditoria)
        if entidade is not None:
            query = query.where(LogAuditoria.entidade == entidade)
        if id_entidade is not None:
            query = query.where(LogAuditoria.id_entidade == id_entidade)
        if id_usuario is not None:
            query = query.where(LogAuditoria.id_usuario == id_usuario)
        if acao is not None:
            query = query.where(LogAuditoria.acao == acao)
        if id_unidade is not None:
            query = query.where(LogAuditoria.id_unidade == id_unidade)
        query = query.order_by(LogAuditoria.criado_em.desc()).offset(offset).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

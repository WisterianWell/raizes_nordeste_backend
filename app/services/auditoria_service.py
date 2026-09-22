from sqlalchemy.ext.asyncio import AsyncSession

from app.database import sessionmanager
from app.enums import AcaoAuditoria, TipoUsuario
from app.models.cliente import Cliente
from app.models.funcionario import Funcionario
from app.repositories.log_auditoria_repo import LogAuditoriaRepository
from app.schemas.auditoria_schemas import LogAuditoriaResponse

async def registrar_log(
    acao: AcaoAuditoria,
    entidade: str,
    usuario: Cliente | Funcionario | None = None,
    id_entidade: int | None = None,
    id_unidade: int | None = None,
    detalhes: dict | None = None,
) -> None:
    if isinstance(usuario, Funcionario):
        tipo_usuario, id_usuario = TipoUsuario.FUNCIONARIO.value, usuario.id_funcionario
    elif isinstance(usuario, Cliente):
        tipo_usuario, id_usuario = TipoUsuario.CLIENTE.value, usuario.id_cliente
    else:
        tipo_usuario, id_usuario = None, None
    async with sessionmanager.session() as session:
        await LogAuditoriaRepository(session).create(
            tipo_usuario=tipo_usuario,
            id_usuario=id_usuario,
            acao=acao.value,
            entidade=entidade,
            id_entidade=id_entidade,
            id_unidade=id_unidade,
            detalhes=detalhes,
        )

class AuditoriaService:
    def __init__(self, session: AsyncSession):
        self.repo = LogAuditoriaRepository(session)

    async def get_logs(
        self,
        entidade: str | None = None,
        id_entidade: int | None = None,
        id_usuario: int | None = None,
        acao: str | None = None,
        id_unidade: int | None = None,
        offset: int = 0,
        limit: int = 10,
    ) -> list[LogAuditoriaResponse]:
        logs = await self.repo.get_logs(entidade, id_entidade, id_usuario, acao, id_unidade, offset, limit)
        return [LogAuditoriaResponse.model_validate(log) for log in logs]

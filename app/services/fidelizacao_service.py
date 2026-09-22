from datetime import datetime, timezone

from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.enums import TipoMovPontos
from app.models.cliente import Cliente
from app.models.fidelizacao import Fidelizacao
from app.repositories.cliente_repo import ClienteRepository
from app.repositories.fidelizacao_repo import FidelizacaoRepository
from app.repositories.mov_pontos_repo import MovPontosRepository
from app.schemas.fidelizacao_schemas import FidelizacaoResponse, MovPontosResponse
from app.exceptions import common_errors
from app.exceptions.error_codes import ErrorCodes
from app.exceptions.exceptions import AppException

PONTOS_POR_REAL = 1
DESC_POR_PONTO = 0.1

class FidelizacaoService:
    def __init__(self, session: AsyncSession):
        self.repo = FidelizacaoRepository(session)
        self.cliente_repo = ClienteRepository(session)
        self.mov_pontos_repo = MovPontosRepository(session)

    def _build_response(self, cliente: Cliente, fidelizacao: Fidelizacao) -> FidelizacaoResponse:
        return FidelizacaoResponse(
            id_cliente=cliente.id_cliente,
            pontos=fidelizacao.pontos,
            consent=cliente.consent,
            consent_at=cliente.consent_at,
        )

    async def _get_or_create_fidelizacao(self, id_cliente: int) -> Fidelizacao:
        fidelizacao = await self.repo.get_by_id(id_cliente)
        if not fidelizacao:
            fidelizacao = await self.repo.create(id_cliente=id_cliente, pontos=0)
        return fidelizacao

    async def aceitar_termos(self, id_cliente: int) -> FidelizacaoResponse:
        cliente = await self.cliente_repo.get_by_id(id_cliente)
        if not cliente:
            raise common_errors.cliente_nao_encontrado()
        cliente = await self.cliente_repo.update(
            id_cliente, consent=True, consent_at=datetime.now(timezone.utc)
        )
        fidelizacao = await self._get_or_create_fidelizacao(id_cliente)
        return self._build_response(cliente, fidelizacao)

    async def revogar_termos(self, id_cliente: int) -> FidelizacaoResponse:
        cliente = await self.cliente_repo.get_by_id(id_cliente)
        if not cliente:
            raise common_errors.cliente_nao_encontrado()
        cliente = await self.cliente_repo.update(
            id_cliente, consent=False, consent_at=None
        )
        fidelizacao = await self._get_or_create_fidelizacao(id_cliente)
        return self._build_response(cliente, fidelizacao)

    async def get_fidelizacao(self, id_cliente: int) -> FidelizacaoResponse:
        cliente = await self.cliente_repo.get_by_id(id_cliente)
        if not cliente:
            raise common_errors.cliente_nao_encontrado()
        fidelizacao = await self._get_or_create_fidelizacao(id_cliente)
        return self._build_response(cliente, fidelizacao)

    async def get_movimentacoes(
        self, id_cliente: int, offset: int = 0, limit: int = 10
    ) -> list[MovPontosResponse]:
        if not await self.cliente_repo.get_by_id(id_cliente):
            raise common_errors.cliente_nao_encontrado()
        movimentacoes = await self.mov_pontos_repo.get_by_cliente(id_cliente, offset, limit)
        return [MovPontosResponse.model_validate(m) for m in movimentacoes]

    async def ganhar_pontos(self, id_cliente: int, id_pedido: int, valor: float) -> None:
        cliente = await self.cliente_repo.get_by_id(id_cliente)
        if not cliente or not cliente.consent:
            return
        pontos_ganhos = int(valor * PONTOS_POR_REAL)
        if pontos_ganhos <= 0:
            return
        fidelizacao = await self._get_or_create_fidelizacao(id_cliente)
        await self.repo.update(id_cliente, pontos=fidelizacao.pontos + pontos_ganhos)
        await self.mov_pontos_repo.create(
            id_cliente=id_cliente,
            id_pedido=id_pedido,
            tipo=TipoMovPontos.GANHO.value,
            pontos=pontos_ganhos,
        )

    async def estornar_pontos(self, id_cliente: int, id_pedido: int) -> None:
        ganho = await self.mov_pontos_repo.get_ganho_by_pedido(id_cliente, id_pedido)
        if not ganho:
            return
        fidelizacao = await self.repo.get_by_id(id_cliente)
        if not fidelizacao:
            return
        pontos_a_remover = min(ganho.pontos, fidelizacao.pontos)
        if pontos_a_remover <= 0:
            return
        await self.repo.update(id_cliente, pontos=fidelizacao.pontos - pontos_a_remover)
        await self.mov_pontos_repo.create(
            id_cliente=id_cliente,
            id_pedido=id_pedido,
            tipo=TipoMovPontos.ESTORNO.value,
            pontos=-pontos_a_remover,
        )

    async def calcular_desconto(self, id_cliente: int, pontos: int) -> float:
        if pontos <= 0:
            raise AppException(
                status_code=status.HTTP_400_BAD_REQUEST,
                error_code=ErrorCodes.PONTOS_INVALIDOS,
                message="A quantidade de pontos a resgatar deve ser maior que zero.",
                details=[{
                    "field": "pontos_resgatados",
                    "issue": "Deve ser maior que zero"
                }],
            )
        fidelizacao = await self._get_or_create_fidelizacao(id_cliente)
        if fidelizacao.pontos < pontos:
            raise AppException(
                status_code=status.HTTP_409_CONFLICT,
                error_code=ErrorCodes.SALDO_INSUFICIENTE,
                message="Saldo de pontos insuficiente.",
                details=[{
                    "field": "pontos_resgatados",
                    "issue": f"Saldo disponível: {fidelizacao.pontos}"
                }],
            )
        return pontos * DESC_POR_PONTO

    async def resgatar_pontos(self, id_cliente: int, id_pedido: int, pontos: int) -> None:
        fidelizacao = await self._get_or_create_fidelizacao(id_cliente)
        await self.repo.update(id_cliente, pontos=fidelizacao.pontos - pontos)
        await self.mov_pontos_repo.create(
            id_cliente=id_cliente,
            id_pedido=id_pedido,
            tipo=TipoMovPontos.RESGATE.value,
            pontos=-pontos,
        )

    async def estornar_resgate(self, id_cliente: int, id_pedido: int) -> None:
        resgate = await self.mov_pontos_repo.get_resgate_by_pedido(id_cliente, id_pedido)
        if not resgate:
            return
        fidelizacao = await self.repo.get_by_id(id_cliente)
        if not fidelizacao:
            return
        pontos_a_devolver = -resgate.pontos
        await self.repo.update(id_cliente, pontos=fidelizacao.pontos + pontos_a_devolver)
        await self.mov_pontos_repo.create(
            id_cliente=id_cliente,
            id_pedido=id_pedido,
            tipo=TipoMovPontos.ESTORNO.value,
            pontos=pontos_a_devolver,
        )

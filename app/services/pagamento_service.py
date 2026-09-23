from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.enums import StatusPagamento, StatusPedido
from app.dependencies import verificar_mesma_unidade
from app.models.cliente import Cliente
from app.models.funcionario import Funcionario
from app.repositories.pagamento_repo import PagamentoRepository
from app.repositories.pedido_repo import PedidoRepository
from app.schemas.pagamento_schemas import PagamentoRequest, PagamentoResponse
from app.exceptions import common_errors
from app.exceptions.error_codes import ErrorCodes
from app.exceptions.exceptions import AppException
from app.gateways.pagamento import GatewayPagamentoMock
from app.services.fidelizacao_service import FidelizacaoService

class PagamentoService:
    def __init__(self, session: AsyncSession):
        self.repo = PagamentoRepository(session)
        self.pedido_repo = PedidoRepository(session)
        self.fidelizacao_service = FidelizacaoService(session)
        self.gateway = GatewayPagamentoMock()

    def _verificar_acesso(self, pedido, current_usuario: Cliente | Funcionario) -> None:
        if isinstance(current_usuario, Cliente):
            if current_usuario.id_cliente != pedido.id_cliente:
                raise common_errors.acesso_negado_pedido()
        else:
            verificar_mesma_unidade(current_usuario, pedido.id_unidade)

    async def pagar_pedido(
        self, id_pedido: int, dados: PagamentoRequest, current_usuario: Cliente | Funcionario
    ) -> PagamentoResponse:
        pedido = await self.pedido_repo.get_by_id(id_pedido)
        if not pedido:
            raise common_errors.pedido_nao_encontrado()
        self._verificar_acesso(pedido, current_usuario)
        if pedido.status == StatusPedido.CANCELADO.value:
            raise AppException(
                status_code=status.HTTP_409_CONFLICT,
                error_code=ErrorCodes.PEDIDO_CANCELADO,
                message="Pedido cancelado não pode ser pago.",
                details=[{
                    "field": "status",
                    "issue": "Pedido possui status CANCELADO",
                }],
            )
        pagamentos_existentes = await self.repo.get_by_pedido(id_pedido)
        if any(p.status == StatusPagamento.APROVADO.value for p in pagamentos_existentes):
            raise AppException(
                status_code=status.HTTP_409_CONFLICT,
                error_code=ErrorCodes.PEDIDO_JA_PAGO,
                message="Pedido já está pago.",
                details=[{
                    "field": "status_pagamento",
                    "issue": "Pedido já possui pagamento aprovado",
                }],
            )
        valor_original = float(pedido.valor_total)
        valor = valor_original
        pontos_resgatados = dados.pontos_resgatados or 0
        if pontos_resgatados:
            if pedido.id_cliente is None:
                raise AppException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    error_code=ErrorCodes.CLIENTE_OBRIGATORIO,
                    message="Pedido sem cliente associado não pode resgatar pontos.",
                    details=[{
                        "field": "pontos_resgatados",
                        "issue": "Pedido sem cliente associado não pode resgatar pontos",
                    }],
                )
            desconto = await self.fidelizacao_service.calcular_desconto(pedido.id_cliente, pontos_resgatados)
            valor = max(0.0, valor - desconto)

        payload = self.gateway.processar_pagamento(
            id_pedido, valor, dados.forma_pagamento, force_status=dados.force_status
        )
        pagamento = await self.repo.create(
            id_pedido=id_pedido,
            forma_pagamento=dados.forma_pagamento,
            valor_original=valor_original,
            valor=valor,
            status=payload["status"],
            id_transacao=payload["id_transacao"],
        )
        await self.pedido_repo.update(id_pedido, status_pagamento=pagamento.status)
        if pagamento.status == StatusPagamento.APROVADO.value:
            if pontos_resgatados:
                await self.fidelizacao_service.resgatar_pontos(pedido.id_cliente, id_pedido, pontos_resgatados)
            if pedido.id_cliente is not None:
                await self.fidelizacao_service.ganhar_pontos(pedido.id_cliente, id_pedido, valor)
        return PagamentoResponse.model_validate(pagamento)

    async def get_pagamentos_by_pedido(
        self, id_pedido: int, current_usuario: Cliente | Funcionario, offset: int = 0, limit: int = 10
    ) -> list[PagamentoResponse]:
        pedido = await self.pedido_repo.get_by_id(id_pedido)
        if not pedido:
            raise common_errors.pedido_nao_encontrado()
        self._verificar_acesso(pedido, current_usuario)
        pagamentos = await self.repo.get_by_pedido(id_pedido, offset, limit)
        return [PagamentoResponse.model_validate(pagamento) for pagamento in pagamentos]

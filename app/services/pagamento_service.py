from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.enums import StatusPagamento, StatusPedido
from app.models.cliente import Cliente
from app.models.funcionario import Funcionario
from app.repositories.pagamento_repo import PagamentoRepository
from app.repositories.pedido_repo import PedidoRepository
from app.schemas.pagamento_schemas import PagamentoRequest, PagamentoResponse
from app.gateways.pagamento import GatewayPagamentoMock

class PagamentoService:
    def __init__(self, session: AsyncSession):
        self.repo = PagamentoRepository(session)
        self.pedido_repo = PedidoRepository(session)
        self.gateway = GatewayPagamentoMock()

    def _verify_cliente(self, id_cliente: int | None, current_usuario: Cliente | Funcionario) -> None:
        if isinstance(current_usuario, Cliente) and current_usuario.id_cliente != id_cliente:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você só pode acessar os seus próprios pedidos."
            )

    async def pagar_pedido(
        self, id_pedido: int, dados: PagamentoRequest, current_usuario: Cliente | Funcionario
    ) -> PagamentoResponse:
        pedido = await self.pedido_repo.get_by_id(id_pedido)
        if not pedido:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pedido não encontrado."
            )
        self._verify_cliente(pedido.id_cliente, current_usuario)
        if pedido.status == StatusPedido.CANCELADO.value:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Pedido cancelado não pode ser pago."
            )
        pagamentos_existentes = await self.repo.get_by_pedido(id_pedido)
        if any(p.status == StatusPagamento.APROVADO.value for p in pagamentos_existentes):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Pedido já está pago."
            )
        payload = self.gateway.processar_pagamento(
            id_pedido, float(pedido.valor_total), dados.forma_pagamento, force_status=dados.force_status
        )
        pagamento = await self.repo.create(
            id_pedido=id_pedido,
            forma_pagamento=dados.forma_pagamento,
            valor=pedido.valor_total,
            status=payload["status"],
            id_transacao=payload["id_transacao"],
        )
        return PagamentoResponse.model_validate(pagamento)

    async def get_pagamentos_by_pedido(
        self, id_pedido: int, current_usuario: Cliente | Funcionario, offset: int = 0, limit: int = 10
    ) -> list[PagamentoResponse]:
        pedido = await self.pedido_repo.get_by_id(id_pedido)
        if not pedido:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pedido não encontrado."
            )
        self._verify_cliente(pedido.id_cliente, current_usuario)
        pagamentos = await self.repo.get_by_pedido(id_pedido, offset, limit)
        return [PagamentoResponse.model_validate(pagamento) for pagamento in pagamentos]

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.enums import CanalPedido, StatusPagamento, StatusPedido, TipoMovEstoque
from app.cargos import CARGOS_ADMIN
from app.gateways.pagamento import GatewayPagamentoMock
from app.models.cliente import Cliente
from app.models.funcionario import Funcionario
from app.repositories.cardapio_repo import CardapioRepository
from app.repositories.cliente_repo import ClienteRepository
from app.repositories.estoque_repo import EstoqueRepository
from app.repositories.mov_estoque_repo import MovEstoqueRepository
from app.repositories.pagamento_repo import PagamentoRepository
from app.repositories.pedido_repo import PedidoRepository
from app.repositories.unidade_repo import UnidadeRepository
from app.schemas.pedido_schemas import PedidoRequest, PedidoResponse
from app.services.fidelizacao_service import FidelizacaoService
from app.services.promocao_service import PromocaoService

STATUS_FINALIZADOS = {StatusPedido.ENTREGUE.value, StatusPedido.CANCELADO.value}
CANAIS_CLIENTE_OBRIGATORIO = {CanalPedido.APP.value, CanalPedido.WEB.value, CanalPedido.PICKUP.value}
ORDEM_STATUS = [
    StatusPedido.PENDENTE.value,
    StatusPedido.EM_PREPARO.value,
    StatusPedido.PRONTO.value,
    StatusPedido.ENTREGUE.value,
]

class PedidoService:
    def __init__(self, session: AsyncSession):
        self.repo = PedidoRepository(session)
        self.cliente_repo = ClienteRepository(session)
        self.unidade_repo = UnidadeRepository(session)
        self.cardapio_repo = CardapioRepository(session)
        self.estoque_repo = EstoqueRepository(session)
        self.pagamento_repo = PagamentoRepository(session)
        self.mov_estoque_repo = MovEstoqueRepository(session)
        self.fidelizacao_service = FidelizacaoService(session)
        self.promocao_service = PromocaoService(session)
        self.gateway = GatewayPagamentoMock()

    def _verify_cliente(self, id_cliente: int | None, current_usuario: Cliente | Funcionario) -> None:
        if isinstance(current_usuario, Cliente) and current_usuario.id_cliente != id_cliente:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você só pode acessar os seus próprios pedidos."
            )

    async def create_pedido(self, dados: PedidoRequest, current_usuario: Cliente | Funcionario) -> PedidoResponse:
        if isinstance(current_usuario, Cliente):
            id_cliente = current_usuario.id_cliente
        else:
            id_cliente = dados.id_cliente
            if id_cliente is None and dados.canal in CANAIS_CLIENTE_OBRIGATORIO:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="id_cliente é obrigatório para esse canal de pedido."
                )
        if id_cliente is not None and not await self.cliente_repo.get_by_id(id_cliente):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente não encontrado."
            )
        if not await self.unidade_repo.get_by_id(dados.id_unidade):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Unidade não encontrada."
            )
        itens_list = []
        valor_total = 0
        for item in dados.itens:
            cardapio_item = await self.cardapio_repo.get_item_cardapio(item.id_produto, dados.id_unidade)
            if not cardapio_item or not cardapio_item.disponivel:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"{item.id_produto} não está disponível no cardápio dessa unidade."
                )
            estoque_item = await self.estoque_repo.get_item_estoque(item.id_produto, dados.id_unidade)
            if not estoque_item or estoque_item.quantidade < item.quantidade:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"{item.id_produto} possui estoque insuficiente."
                )
            preco_unitario = await self.promocao_service.calc_preco_desconto(
                item.id_produto, dados.id_unidade, float(cardapio_item.preco)
            )
            valor_total += preco_unitario * item.quantidade
            itens_list.append({
                "id_produto": item.id_produto,
                "quantidade": item.quantidade,
                "preco_unitario": preco_unitario,
            })
            await self.estoque_repo.update_item_estoque(
                item.id_produto, dados.id_unidade, quantidade=estoque_item.quantidade - item.quantidade
            )
        pedido = await self.repo.create_pedido(
            itens=itens_list,
            id_cliente=id_cliente,
            id_unidade=dados.id_unidade,
            canal=dados.canal,
            status=StatusPedido.PENDENTE.value,
            valor_total=valor_total,
        )
        for item in itens_list:
            await self.mov_estoque_repo.create(
                id_produto=item["id_produto"],
                id_unidade=dados.id_unidade,
                id_pedido=pedido.id_pedido,
                tipo=TipoMovEstoque.VENDA.value,
                quantidade=-item["quantidade"],
            )
        return PedidoResponse.model_validate(pedido)

    async def get_pedido_by_id(self, id_pedido: int, current_usuario: Cliente | Funcionario) -> PedidoResponse:
        pedido = await self.repo.get_by_id(id_pedido)
        if not pedido:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pedido não encontrado."
            )
        self._verify_cliente(pedido.id_cliente, current_usuario)
        return PedidoResponse.model_validate(pedido)

    async def get_pedidos(
        self,
        current_usuario: Cliente | Funcionario,
        id_cliente: int | None = None,
        id_unidade: int | None = None,
        canal: str | None = None,
        offset: int = 0,
        limit: int = 10,
    ) -> list[PedidoResponse]:
        if isinstance(current_usuario, Cliente):
            id_cliente = current_usuario.id_cliente
        elif current_usuario.cargo not in CARGOS_ADMIN and id_unidade is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Informe id_unidade para listar pedidos com esse cargo."
            )
        pedidos = await self.repo.get_pedidos(
            id_cliente=id_cliente, id_unidade=id_unidade, canal=canal, offset=offset, limit=limit
        )
        return [PedidoResponse.model_validate(pedido) for pedido in pedidos]

    async def avancar_status_pedido(self, id_pedido: int) -> PedidoResponse:
        pedido = await self.repo.get_by_id(id_pedido)
        if not pedido:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pedido não encontrado."
            )
        if pedido.status in STATUS_FINALIZADOS:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Pedido já finalizado e não pode ter o status alterado."
            )
        indice_atual = ORDEM_STATUS.index(pedido.status)
        proximo_status = ORDEM_STATUS[indice_atual + 1]
        pedido = await self.repo.update_status_pedido(id_pedido, proximo_status)
        return PedidoResponse.model_validate(pedido)

    async def cancelar_pedido(self, id_pedido: int, current_usuario: Cliente | Funcionario) -> PedidoResponse:
        pedido = await self.repo.get_by_id(id_pedido)
        if not pedido:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pedido não encontrado."
            )
        self._verify_cliente(pedido.id_cliente, current_usuario)
        if pedido.status in STATUS_FINALIZADOS:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Pedido já finalizado e não pode ser cancelado."
            )
        for item in pedido.itens:
            estoque_item = await self.estoque_repo.get_item_estoque(item.id_produto, pedido.id_unidade)
            if estoque_item:
                await self.estoque_repo.update_item_estoque(
                    item.id_produto, pedido.id_unidade, quantidade=estoque_item.quantidade + item.quantidade
                )
                await self.mov_estoque_repo.create(
                    id_produto=item.id_produto,
                    id_unidade=pedido.id_unidade,
                    id_pedido=pedido.id_pedido,
                    tipo=TipoMovEstoque.CANCELAMENTO.value,
                    quantidade=item.quantidade,
                )
        pagamento_aprovado = next(
            (p for p in pedido.pagamentos if p.status == StatusPagamento.APROVADO.value), None
        )
        if pagamento_aprovado:
            payload = self.gateway.estornar_pagamento(pagamento_aprovado.id_transacao, float(pagamento_aprovado.valor))
            await self.pagamento_repo.create(
                id_pedido=id_pedido,
                forma_pagamento=pagamento_aprovado.forma_pagamento,
                valor_original=pagamento_aprovado.valor_original,
                valor=pagamento_aprovado.valor,
                status=payload["status"],
                id_transacao=payload["id_transacao"],
            )
            await self.repo.update(id_pedido, status_pagamento=payload["status"])
            if pedido.id_cliente is not None:
                await self.fidelizacao_service.estornar_pontos(pedido.id_cliente, id_pedido)
                await self.fidelizacao_service.estornar_resgate(pedido.id_cliente, id_pedido)
        pedido = await self.repo.update_status_pedido(id_pedido, StatusPedido.CANCELADO.value)
        return PedidoResponse.model_validate(pedido)

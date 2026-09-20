from datetime import datetime

from pydantic import BaseModel, Field

from app.enums import CanalPedido
from app.schemas.pagamento_schemas import PagamentoResponse

class ItemPedidoRequest(BaseModel):
    id_produto: int
    quantidade: int = Field(gt=0)

class ItemPedidoResponse(BaseModel):
    id_produto: int
    nome_produto: str
    quantidade: int
    preco_unitario: float
    subtotal: float
    model_config = {"from_attributes": True}

class PedidoRequest(BaseModel):
    id_cliente: int | None = None
    id_unidade: int
    canal: CanalPedido
    itens: list[ItemPedidoRequest] = Field(min_length=1)
    model_config = {"use_enum_values": True}

class PedidoResponse(BaseModel):
    id_pedido: int
    id_cliente: int | None
    id_unidade: int
    canal: str
    status: str
    status_pagamento: str | None
    valor_total: float
    created_at: datetime
    itens: list[ItemPedidoResponse]
    pagamentos: list[PagamentoResponse]
    model_config = {"from_attributes": True}

from datetime import datetime

from pydantic import BaseModel

from app.domain.enums import FormaPagamento, StatusPagamento

class PagamentoRequest(BaseModel):
    forma_pagamento: FormaPagamento
    force_status: StatusPagamento | None = None
    pontos_resgatados: int | None = None
    model_config = {"use_enum_values": True}

class PagamentoResponse(BaseModel):
    id_pagamento: int
    id_pedido: int
    id_transacao: str
    forma_pagamento: str
    valor_original: float
    valor: float
    status: str
    created_at: datetime
    model_config = {"from_attributes": True}

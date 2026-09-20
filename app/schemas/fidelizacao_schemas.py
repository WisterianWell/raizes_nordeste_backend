from datetime import datetime

from pydantic import BaseModel

class FidelizacaoResponse(BaseModel):
    id_cliente: int
    pontos: int
    consent: bool
    consent_at: datetime | None
    model_config = {"from_attributes": True}

class MovPontosResponse(BaseModel):
    id_movimentacao: int
    id_cliente: int
    id_pedido: int | None
    tipo: str
    pontos: int
    created_at: datetime
    model_config = {"from_attributes": True}

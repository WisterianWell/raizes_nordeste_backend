from datetime import datetime

from pydantic import BaseModel, Field

class MovEstoqueRequest(BaseModel):
    quantidade: int = Field(gt=0)

class MovEstoqueResponse(BaseModel):
    id_movimentacao: int
    id_produto: int
    id_unidade: int
    id_pedido: int | None
    tipo: str
    quantidade: int
    created_at: datetime
    model_config = {"from_attributes": True}

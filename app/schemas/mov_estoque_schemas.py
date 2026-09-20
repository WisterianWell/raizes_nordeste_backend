from datetime import datetime

from pydantic import BaseModel, Field

class ItemMovEstoqueRequest(BaseModel):
    id_produto: int
    id_unidade: int
    quantidade: int = Field(gt=0)

class MovEstoqueRequest(BaseModel):
    itens: list[ItemMovEstoqueRequest] = Field(min_length=1)

class MovEstoqueResponse(BaseModel):
    id_movimentacao: int
    id_produto: int
    id_unidade: int
    id_pedido: int | None
    tipo: str
    quantidade: int
    created_at: datetime
    model_config = {"from_attributes": True}

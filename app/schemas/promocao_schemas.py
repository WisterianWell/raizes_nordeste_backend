from datetime import datetime

from pydantic import BaseModel, Field

from app.enums import TipoDesconto

class ItemPromocaoRequest(BaseModel):
    id_produto: int
    tipo_valor: TipoDesconto
    valor_desc: float = Field(gt=0)
    model_config = {"use_enum_values": True}

class ItemPromocaoResponse(BaseModel):
    id_produto: int
    nome_produto: str
    tipo_valor: str
    valor_desc: float
    model_config = {"from_attributes": True}

class PromocaoRequest(BaseModel):
    id_unidade: int | None = None
    data_inicio: datetime
    data_fim: datetime
    itens: list[ItemPromocaoRequest] = Field(min_length=1)
    model_config = {"use_enum_values": True}

class PromocaoUpdate(BaseModel):
    id_unidade: int | None = None
    data_inicio: datetime | None = None
    data_fim: datetime | None = None
    ativo: bool | None = None
    itens: list[ItemPromocaoRequest] | None = None
    model_config = {"use_enum_values": True}

class PromocaoResponse(BaseModel):
    id_promocao: int
    id_unidade: int | None
    data_inicio: datetime
    data_fim: datetime
    ativo: bool
    created_at: datetime
    itens: list[ItemPromocaoResponse]
    model_config = {"from_attributes": True}

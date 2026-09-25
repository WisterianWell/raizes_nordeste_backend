from pydantic import BaseModel

class CardapioRequest(BaseModel):
    id_produto: int
    id_unidade: int
    preco: float
    estoque: int = 0
    ativo: bool = True

class CardapioUpdate(BaseModel):
    preco: float | None = None
    ativo: bool | None = None

class CardapioResponse(BaseModel):
    id_produto: int
    id_unidade: int
    nome: str
    categoria: str
    preco: float
    preco_promo: float | None
    estoque: int
    ativo: bool
    model_config = {"from_attributes": True}

class CardapioPublicoResponse(BaseModel):
    id_produto: int
    id_unidade: int
    nome: str
    categoria: str
    preco: float
    preco_promo: float | None
    ativo: bool
    model_config = {"from_attributes": True}

from pydantic import BaseModel

class CardapioRequest(BaseModel):
    id_produto: int
    id_unidade: int
    preco: float
    estoque: int = 0
    disponivel: bool = True

class CardapioUpdate(BaseModel):
    preco: float | None = None
    disponivel: bool | None = None

class CardapioResponse(BaseModel):
    id_produto: int
    id_unidade: int
    nome: str
    categoria: str
    preco: float
    estoque: int
    disponivel: bool
    model_config = {"from_attributes": True}

class CardapioPublicoResponse(BaseModel):
    id_produto: int
    id_unidade: int
    nome: str
    categoria: str
    preco: float
    disponivel: bool
    model_config = {"from_attributes": True}

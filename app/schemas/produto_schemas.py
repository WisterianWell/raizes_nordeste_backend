from pydantic import BaseModel

class ProdutoRequest(BaseModel):
    nome: str
    categoria: str

class ProdutoUpdate(BaseModel):
    nome: str | None = None
    categoria: str | None = None

class ProdutoResponse(BaseModel):
    id_produto: int
    nome: str
    categoria: str
    model_config = {"from_attributes": True}

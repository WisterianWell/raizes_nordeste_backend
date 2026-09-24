from pydantic import BaseModel

class UnidadeRequest(BaseModel):
    nome: str
    endereco: str
    telefone: str
    esta_aberta: bool = True

class UnidadeUpdate(BaseModel):
    nome: str | None = None
    endereco: str | None = None
    telefone: str | None = None

class UnidadeResponse(BaseModel):
    id_unidade: int
    nome: str
    endereco: str
    telefone: str
    esta_aberta: bool
    model_config = {"from_attributes": True}

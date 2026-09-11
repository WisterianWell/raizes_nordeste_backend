from pydantic import BaseModel

class UnidadeRequest(BaseModel):
    nome: str
    endereco: str
    telefone: str

class UnidadeUpdate(BaseModel):
    nome: str | None = None
    endereco: str | None = None
    telefone: str | None = None

class UnidadeResponse(BaseModel):
    id_unidade: int
    nome: str
    endereco: str
    telefone: str
    model_config = {"from_attributes": True}

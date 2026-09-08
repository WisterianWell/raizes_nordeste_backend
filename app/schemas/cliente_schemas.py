from pydantic import BaseModel

class ClienteRequest(BaseModel):
    nome: str
    email: str
    cpf: str
    telefone: str
    senha: str

class ClienteUpdate(BaseModel):
    nome: str | None = None
    email: str | None = None
    cpf: str | None = None
    telefone: str | None = None
    senha: str | None = None

class ClienteResponse(BaseModel):
    id_cliente: int
    nome: str
    email: str
    cpf: str
    telefone: str
    model_config = {"from_attributes": True}

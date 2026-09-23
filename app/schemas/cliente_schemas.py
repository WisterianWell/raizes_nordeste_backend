from pydantic import BaseModel, EmailStr

class ClienteRequest(BaseModel):
    nome: str
    email: EmailStr
    cpf: str | None = None
    telefone: str
    senha: str

class ClienteUpdate(BaseModel):
    nome: str | None = None
    email: EmailStr | None = None
    cpf: str | None = None
    telefone: str | None = None
    senha: str | None = None

class ClienteResponse(BaseModel):
    id_cliente: int
    nome: str
    email: EmailStr
    cpf: str | None
    telefone: str
    model_config = {"from_attributes": True}

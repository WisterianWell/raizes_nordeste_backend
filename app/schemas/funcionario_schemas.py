from pydantic import BaseModel, EmailStr

from app.enums import CargoFunc

class FuncionarioRequest(BaseModel):
    id_unidade: int
    nome: str
    email: EmailStr
    cpf: str
    telefone: str
    senha: str
    cargo: CargoFunc
    model_config = {"use_enum_values": True}

class FuncionarioUpdate(BaseModel):
    nome: str | None = None
    email: EmailStr | None = None
    cpf: str | None = None
    telefone: str | None = None
    senha: str | None = None
    cargo: CargoFunc | None = None
    model_config = {"use_enum_values": True}

class FuncionarioResponse(BaseModel):
    id_funcionario: int
    id_unidade: int | None
    nome: str
    email: EmailStr
    cpf: str
    telefone: str
    cargo: str
    model_config = {"from_attributes": True}

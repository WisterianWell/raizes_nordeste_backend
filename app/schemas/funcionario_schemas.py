from pydantic import BaseModel, EmailStr

from app.repositories.enums import CargoFuncionario

class FuncionarioRequest(BaseModel):
    nome: str
    email: EmailStr
    cpf: str
    telefone: str
    senha: str
    cargo: CargoFuncionario
    model_config = {"use_enum_values": True}

class FuncionarioUpdate(BaseModel):
    nome: str | None = None
    email: EmailStr | None = None
    cpf: str | None = None
    telefone: str | None = None
    senha: str | None = None
    cargo: CargoFuncionario | None = None
    model_config = {"use_enum_values": True}

class FuncionarioResponse(BaseModel):
    id_funcionario: int
    nome: str
    email: EmailStr
    cpf: str
    telefone: str
    cargo: str
    model_config = {"from_attributes": True}

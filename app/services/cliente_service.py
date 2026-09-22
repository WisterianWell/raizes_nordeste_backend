from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.cliente_repo import ClienteRepository
from app.schemas.cliente_schemas import ClienteRequest, ClienteResponse, ClienteUpdate
from app.exceptions import common_errors
from app.core.security import get_senha_hash

class ClienteService:
    def __init__(self, session: AsyncSession):
        self.repo = ClienteRepository(session)

    async def create_cliente(self, cliente: ClienteRequest) -> ClienteResponse:
        existing_cliente = await self.repo.get_by_email(cliente.email)
        if existing_cliente:
            raise common_errors.email_ja_cadastrado()
        existing_cpf = await self.repo.get_by_cpf(cliente.cpf)
        if existing_cpf:
            raise common_errors.cpf_ja_cadastrado()
        cliente = await self.repo.create(
            nome=cliente.nome,
            email=cliente.email,
            cpf=cliente.cpf,
            telefone=cliente.telefone,
            hashed_senha=get_senha_hash(cliente.senha)
        )
        return ClienteResponse.model_validate(cliente)

    async def get_cliente_by_id(self, id_cliente: int) -> ClienteResponse:
        cliente = await self.repo.get_by_id(id_cliente)
        if not cliente:
            raise common_errors.cliente_nao_encontrado()
        return ClienteResponse.model_validate(cliente)

    async def get_all_clientes(self, offset: int = 0, limit: int = 10) -> list[ClienteResponse]:
        clientes = await self.repo.get_all_clientes(offset, limit)
        return [ClienteResponse.model_validate(cliente) for cliente in clientes]

    async def update_cliente(self, id_cliente: int, dados: ClienteUpdate) -> ClienteResponse:
        cliente = await self.repo.get_by_id(id_cliente)
        if not cliente:
            raise common_errors.cliente_nao_encontrado()
        update_data = dados.model_dump(exclude_unset=True)
        if "email" in update_data:
            existing_email = await self.repo.get_by_email(update_data["email"])
            if existing_email and existing_email.id_cliente != id_cliente:
                raise common_errors.email_ja_cadastrado()
        if "cpf" in update_data:
            existing_cpf = await self.repo.get_by_cpf(update_data["cpf"])
            if existing_cpf and existing_cpf.id_cliente != id_cliente:
                raise common_errors.cpf_ja_cadastrado()
        if "senha" in update_data:
            update_data["hashed_senha"] = get_senha_hash(update_data.pop("senha"))
        cliente = await self.repo.update(id_cliente, **update_data)
        return ClienteResponse.model_validate(cliente)

    async def delete_cliente(self, id_cliente: int) -> None:
        deleted = await self.repo.delete(id_cliente)
        if not deleted:
            raise common_errors.cliente_nao_encontrado()

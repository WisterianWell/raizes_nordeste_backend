from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.funcionario_repo import FuncionarioRepository
from app.repositories.unidade_repo import UnidadeRepository
from app.schemas.funcionario_schemas import FuncionarioResponse, FuncionarioRequest, FuncionarioUpdate
from app.exceptions import common_errors
from app.core.security import get_senha_hash

class FuncionarioService:
    def __init__(self, session: AsyncSession):
        self.repo = FuncionarioRepository(session)
        self.unidade_repo = UnidadeRepository(session)

    async def create_funcionario(self, funcionario: FuncionarioRequest) -> FuncionarioResponse:
        existing_funcionario = await self.repo.get_by_email(funcionario.email)
        if existing_funcionario:
            raise common_errors.email_ja_cadastrado()
        existing_cpf = await self.repo.get_by_cpf(funcionario.cpf)
        if existing_cpf:
            raise common_errors.cpf_ja_cadastrado()
        unidade = await self.unidade_repo.get_by_id(funcionario.id_unidade)
        if not unidade:
            raise common_errors.unidade_nao_encontrada()
        funcionario = await self.repo.create(
            id_unidade=funcionario.id_unidade,
            nome=funcionario.nome,
            email=funcionario.email,
            cpf=funcionario.cpf,
            telefone=funcionario.telefone,
            hashed_senha=get_senha_hash(funcionario.senha),
            cargo=funcionario.cargo
        )
        return FuncionarioResponse.model_validate(funcionario)

    async def get_funcionario_by_id(self, id_funcionario: int) -> FuncionarioResponse:
        funcionario = await self.repo.get_by_id(id_funcionario)
        if not funcionario:
            raise common_errors.funcionario_nao_encontrado()
        return FuncionarioResponse.model_validate(funcionario)

    async def get_funcionarios(
        self, id_unidade: int | None = None, offset: int = 0, limit: int = 10
    ) -> list[FuncionarioResponse]:
        if id_unidade is not None and not await self.unidade_repo.get_by_id(id_unidade):
            raise common_errors.unidade_nao_encontrada()
        funcionarios = await self.repo.get_funcionarios(id_unidade, offset, limit)
        return [FuncionarioResponse.model_validate(funcionario) for funcionario in funcionarios]

    async def update_funcionario(self, id_funcionario: int, dados: FuncionarioUpdate) -> FuncionarioResponse:
        funcionario = await self.repo.get_by_id(id_funcionario)
        if not funcionario:
            raise common_errors.funcionario_nao_encontrado()
        update_data = dados.model_dump(exclude_unset=True)
        if "email" in update_data:
            existing_email = await self.repo.get_by_email(update_data["email"])
            if existing_email and existing_email.id_funcionario != id_funcionario:
                raise common_errors.email_ja_cadastrado()
        if "cpf" in update_data:
            existing_cpf = await self.repo.get_by_cpf(update_data["cpf"])
            if existing_cpf and existing_cpf.id_funcionario != id_funcionario:
                raise common_errors.cpf_ja_cadastrado()
        if "id_unidade" in update_data:
            unidade = await self.unidade_repo.get_by_id(update_data["id_unidade"])
            if not unidade:
                raise common_errors.unidade_nao_encontrada()
        if "senha" in update_data:
            update_data["hashed_senha"] = get_senha_hash(update_data.pop("senha"))
        funcionario = await self.repo.update(id_funcionario, **update_data)
        return FuncionarioResponse.model_validate(funcionario)

    async def delete_funcionario(self, id_funcionario: int) -> None:
        deleted = await self.repo.delete(id_funcionario)
        if not deleted:
            raise common_errors.funcionario_nao_encontrado()

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.unidade_repo import UnidadeRepository
from app.schemas.unidade_schemas import UnidadeRequest, UnidadeResponse, UnidadeUpdate

class UnidadeService:
    def __init__(self, session: AsyncSession):
        self.repo = UnidadeRepository(session)

    async def create_unidade(self, unidade: UnidadeRequest) -> UnidadeResponse:
        nova_unidade = await self.repo.create(
            nome=unidade.nome,
            endereco=unidade.endereco,
            telefone=unidade.telefone,
        )
        return UnidadeResponse.model_validate(nova_unidade)

    async def get_unidade_by_id(self, id_unidade: int) -> UnidadeResponse:
        unidade = await self.repo.get_by_id(id_unidade)
        if not unidade:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Unidade não encontrada."
            )
        return UnidadeResponse.model_validate(unidade)

    async def get_all_unidades(self, offset: int = 0, limit: int = 100) -> list[UnidadeResponse]:
        unidades = await self.repo.get_all_unidades(offset, limit)
        return [UnidadeResponse.model_validate(unidade) for unidade in unidades]

    async def update_unidade(self, id_unidade: int, dados: UnidadeUpdate) -> UnidadeResponse:
        unidade = await self.repo.get_by_id(id_unidade)
        if not unidade:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Unidade não encontrada."
            )
        update_data = dados.model_dump(exclude_unset=True)
        unidade = await self.repo.update(id_unidade, **update_data)
        return UnidadeResponse.model_validate(unidade)

    async def delete_unidade(self, id_unidade: int) -> None:
        deleted = await self.repo.delete(id_unidade)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Unidade não encontrada."
            )

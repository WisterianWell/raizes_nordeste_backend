from typing import Generic, TypeVar, Type
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)

class BaseRepository(Generic[ModelType]):

    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def get_by_id(self, id: int) -> ModelType | None:
        return await self.session.get(self.model, id)

    async def get_all(
        self, offset: int = 0, limit: int = 100
    ) -> list[ModelType]:
        query = select(self.model).offset(offset).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def create(self, **kwargs) -> ModelType:
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def update(
        self, id: int, **kwargs
    ) -> ModelType | None:
        instance = await self.get_by_id(id)
        if not instance:
            return None
        for key, value in kwargs.items():
            setattr(instance, key, value)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def delete(self, id: int) -> bool:
        instance = await self.get_by_id(id)
        if not instance:
            return False
        await self.session.delete(instance)
        await self.session.flush()
        return True

    async def count(self) -> int:
        query = select(func.count()).select_from(self.model)
        result = await self.session.execute(query)
        return result.scalar_one()
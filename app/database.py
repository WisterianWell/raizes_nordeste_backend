from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


class DatabaseSessionManager:

    def __init__(self):
        self._engine = None
        self._sessionmaker = None

    async def init(self, database_url: str):
        self._engine = create_async_engine(
            database_url,
            pool_size=20,
            max_overflow=10,
            pool_pre_ping=True,
            echo=False
        )
        self._sessionmaker = async_sessionmaker(
            bind=self._engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

    async def close(self):
        if self._engine:
            await self._engine.dispose()

    async def create_all(self, base) -> None:
        async with self._engine.begin() as conn:
            await conn.run_sync(base.metadata.create_all)

    @asynccontextmanager
    async def session(self):
        if self._sessionmaker is None:
            raise RuntimeError("DatabaseSessionManager não foi inicializado")

        async with self._sessionmaker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

sessionmanager = DatabaseSessionManager()

async def get_db_session():
    async with sessionmanager.session() as session:
        yield session

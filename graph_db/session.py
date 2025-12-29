from typing import Iterator
from common.config import settings
from fastapi import Depends
from typing_extensions import Annotated
from sqlalchemy.orm.session import Session
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine

engine: Engine = create_engine(
    str(settings.DATABASE_URI), echo=True, pool_pre_ping=True
)
SessionMaker = sessionmaker(bind=engine, expire_on_commit=False)

async_database_uri = str(settings.DATABASE_URI).replace(
    "postgresql://", "postgresql+asyncpg://"
)
async_engine: Engine = create_async_engine(
    async_database_uri, pool_pre_ping=True, echo=True
)
AsyncSessionMaker = sessionmaker(
    bind=async_engine, expire_on_commit=False, class_=AsyncSession
)


def get_sync_session() -> Session:
    """Returns a new synchronous session, manually managed."""
    return SessionMaker()


def get_async_session() -> AsyncSession:
    """Returns a new asynchronous session."""
    return AsyncSessionMaker()


def get_db_session() -> Iterator[Session]:
    session: Session = SessionMaker()

    try:
        yield session
    finally:
        session.close()


DBSession = Annotated[Session, Depends(get_db_session)]


async def get_async_db_session():
    # def get_async_db_session() -> Iterator[Session]:
    # session: Session = AsyncSessionMaker()

    # try:
    #     yield session
    # finally:
    #     session.close()

    async with AsyncSessionMaker() as session:
        async with session.begin():
            try:
                yield session
            finally:
                await session.close()


AsyncDBSession = Annotated[AsyncSession, Depends(get_async_db_session)]


# AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# @asynccontextmanager
# async def get_async_session():
#     async with AsyncSessionLocal() as session:
#         yield session  # Yield session to be used in async functions


# engine_: AsyncEngine = create_async_engine(str(settings.DATABASE_URI))
# SessionMaker_ = sessionmaker(
#     bind=engine_,
#     class_=AsyncSession,
#     expire_on_commit=False,
#     autocommit=False,
#     autoflush=False,
# )

# @asynccontextmanager
# async def get_async_db_session() -> AsyncGenerator[AsyncSession, None]:
#     async with SessionMaker_() as session:
#         async with session.begin():
#             try:
#                 yield session
#             finally:
#                 await session.close()

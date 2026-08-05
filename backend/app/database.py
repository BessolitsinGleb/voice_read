from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from .core.config import Settings
from sqlalchemy.orm import DeclarativeBase

engine = create_async_engine(Settings.DATABASE_URL, echo=True)
async_session = async_sessionmaker(engine, expire_on_commit=False,class_=AsyncSession)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with async_session() as session:
        yield session
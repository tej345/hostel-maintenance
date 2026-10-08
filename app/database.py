# app/database.py
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.config import settings

# 1. Create Async Engine with Connection Pooling
engine = create_async_engine(
    settings.ASYNC_DATABASE_URL,
    echo=True, # Logs generated SQL queries in terminal (useful for debugging)
    future=True,
)

# 2. Async Session Factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# 3. Base class for SQLAlchemy Models
class Base(DeclarativeBase):
    pass

# 4. Dependency Injection for FastAPI Endpoints
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
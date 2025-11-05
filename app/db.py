import re
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Normalize DATABASE_URL: if provider returns 'postgresql://' replace with
# 'postgresql+asyncpg://' so SQLAlchemy async driver is used.
database_url = re.sub(r'^postgresql:', 'postgresql+asyncpg:', settings.DATABASE_URL)

# Remover parâmetros incompatíveis com asyncpg
database_url = re.sub(r'[?&]channel_binding=\w+', '', database_url)
database_url = database_url.replace('sslmode=require', 'ssl=require')

engine = create_async_engine(database_url, future=True, echo=False)

async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def get_session():
    async with async_session() as session:
        yield session

# Alias para compatibilidade
get_db = get_session

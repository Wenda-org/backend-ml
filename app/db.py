import re
import ssl
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Normalize DATABASE_URL: if provider returns 'postgresql://' replace with
# 'postgresql+asyncpg://' so SQLAlchemy async driver is used.
database_url = re.sub(r'^postgresql:', 'postgresql+asyncpg:', settings.DATABASE_URL)

# Remover parâmetros incompatíveis com asyncpg
database_url = re.sub(r'[?&]channel_binding=\w+', '', database_url)

connect_args = {}
if any(x in database_url for x in ["sslmode=require", "ssl=require", "ssl=true", "ssl=1"]):
    # Remove SSL params from URL to prevent asyncpg driver errors
    database_url = re.sub(r'[?&]ssl(mode)?=\w+', '', database_url)
    
    # Configure default SSL context that bypasses certificate verification for server compatibility
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    connect_args["ssl"] = ctx

# Ensure correct query parameter symbol after removals
if "?" not in database_url and "&" in database_url:
    database_url = database_url.replace("&", "?", 1)

engine = create_async_engine(database_url, connect_args=connect_args, future=True, echo=False)

async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def get_session():
    async with async_session() as session:
        yield session

# Alias para compatibilidade
get_db = get_session

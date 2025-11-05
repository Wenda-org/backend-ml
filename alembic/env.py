from __future__ import with_statement

import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# add app path to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# this is the Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# import your models' MetaData object here for 'autogenerate' support
from app.models import Base
target_metadata = Base.metadata

# other values from the config can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    # use DATABASE_URL from environment if available
    database_url = os.environ.get("DATABASE_URL")
    if database_url:
        # Use asyncpg for migrations (it's already installed)
        if database_url.startswith('postgresql://'):
            database_url = database_url.replace('postgresql://', 'postgresql+asyncpg://')
        elif '+psycopg://' in database_url:
            database_url = database_url.replace('+psycopg://', '+asyncpg://')
        
        # Remove psycopg-specific parameters that asyncpg doesn't understand
        import re
        database_url = re.sub(r'[?&]channel_binding=\w+', '', database_url)
        database_url = database_url.replace('sslmode=require', 'ssl=require')
        
        config.set_main_option('sqlalchemy.url', database_url)

    from sqlalchemy.ext.asyncio import create_async_engine
    import asyncio

    async_engine = create_async_engine(
        config.get_main_option("sqlalchemy.url"),
        poolclass=pool.NullPool,
    )

    async def run_async_migrations():
        async with async_engine.connect() as connection:
            await connection.run_sync(do_run_migrations)
        await async_engine.dispose()

    def do_run_migrations(connection):
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

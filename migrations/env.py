from logging.config import fileConfig

import alembic
from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from db.config import Base, DATABASE_URL
from db.models import User, Task, metadata

url=DATABASE_URL#"postgresql+asyncpg://postgres:postgres@localhost/task_note_db"


async def get_async_session():
    engine = create_async_engine(url)
    async with engine.scoped_session(model=Base) as session:
        yield session

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
# target_metadata = metadata
target_metadata = [metadata, Base.metadata]
# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    # url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


# def run_migrations_online() -> None:
#     """Run migrations in 'online' mode.
#
#     In this scenario we need to create an Engine
#     and associate a connection with the context.
#
#     """
#     connectable = engine_from_config(
#         config.get_section(config.config_ini_section, {}),
#         prefix="sqlalchemy.",
#         poolclass=pool.NullPool,
#         url=url,
#     )
#
#     with connectable.connect() as connection:
#         context.configure(
#             connection=connection, target_metadata=target_metadata
#         )
#
#         with context.begin_transaction():
#             context.run_migrations()
async def run_migrations_online():
    """Запуск миграций в онлайн режиме."""

    connectable = create_async_engine(
        url,#config.get_main_option("sqlalchemy.url"),
        future=True,
        echo=True,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def do_run_migrations(connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        render_as_batch=True  # если используете batch mode
    )

    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    # run_migrations_online()
    asyncio.run(run_migrations_online())
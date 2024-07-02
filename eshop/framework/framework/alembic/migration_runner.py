from logging.config import fileConfig
from typing import Type

from alembic import context

from sqlalchemy import create_engine, pool
from sqlalchemy.schema import CreateSchema

from eshop import settings

from framework.app_config import IAppConfig
from framework.sqlalchemy.dialects.postgres.pydantic_type import PydanticType


def init_alembic_logging():
    # this is the Alembic Config object, which provides
    # access to the values within the .ini file in use.
    config = context.config

    # Interpret the config file for Python logging.
    # This line sets up loggers basically.
    if config.config_file_name is not None:
        fileConfig(config.config_file_name)


class MigrationRunner:
    def __init__(self, app_config: Type[IAppConfig]):
        self._app_config = app_config
        self._target_metadata = self._app_config.get_sqlalchemy_base().metadata

    def _include_name(self, name, type_, parent_names):
        if type_ == "schema":
            return name == self._target_metadata.schema
        else:
            return True

    def _render_item(self, type_, obj, autogen_context):
        if type_ == "type" and isinstance(obj, PydanticType):
            return "JSONB()"
        return False

    def _run_migrations_online(self) -> None:
        """Run migrations in 'online' mode.

        In this scenario we need to create an Engine
        and associate a connection with the context.

        """
        engine = create_engine(url=settings.DB_URL, poolclass=pool.NullPool)

        with engine.connect() as connection:
            context.configure(
                connection=connection,
                target_metadata=self._target_metadata,
                version_table_schema=self._target_metadata.schema,
                include_schemas=True,
                include_name=self._include_name,
                render_item=self._render_item,
            )

            connection.execute(CreateSchema(name=self._target_metadata.schema, if_not_exists=True))

            with context.begin_transaction():
                context.run_migrations()

    def _run_migrations_offline(self) -> None:
        """Run migrations in 'offline' mode.

        This configures the context with just a URL
        and not an Engine, though an Engine is acceptable
        here as well.  By skipping the Engine creation
        we don't even need a DBAPI to be available.

        Calls to context.execute() here emit the given string to the
        script output.

        """
        context.configure(
            url=settings.DB_URL,
            target_metadata=self._target_metadata,
            literal_binds=True,
            dialect_opts={"paramstyle": "named"},
            include_schemas=True,
            include_name=self._include_name,
            render_item=self._render_item,
        )

        with context.begin_transaction():
            context.run_migrations()

    def run_migrations(self):
        self._app_config.import_models()
        if context.is_offline_mode():
            self._run_migrations_offline()
        else:
            self._run_migrations_online()


init_alembic_logging()

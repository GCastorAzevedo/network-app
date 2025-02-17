import os
import random
import string

from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context
from alembic.script import ScriptDirectory

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
target_metadata = None

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


ALEMBIC_USERNAME = os.getenv("ALEMBIC_USERNAME")
ALEMBIC_PASSWORD = os.getenv("ALEMBIC_PASSWORD")
DATABASE_NAME = os.getenv("DATABASE_NAME")

if None in [ALEMBIC_USERNAME, ALEMBIC_PASSWORD, DATABASE_NAME]:
    raise ValueError(
        "ALEMBIC_USERNAME, ALEMBIC_PASSWORD, and ALEMBIC_DATABASE_NAME must be set"
    )

HOSTNAME = os.getenv("HOSTNAME") or "localhost"
PORT = os.getenv("PORT") or "5432"

DATABASE_URI = (
    os.getenv("DATABASE_URI")
    or f"postgresql://{ALEMBIC_USERNAME}:{ALEMBIC_PASSWORD}@{HOSTNAME}:{PORT}/{DATABASE_NAME}"
)


def process_revision_directives(context, _, directives):
    """
    Enforces sequential numeric revision IDs when generating new revisions.
    """
    migration_script = directives[0]
    head_revision = ScriptDirectory.from_config(context.config).get_current_head()

    if head_revision is None:
        new_rev_id = 1
    else:
        last_rev_id = int(head_revision[:6].lstrip("0"))
        new_rev_id = last_rev_id + 1

    # S311: non cryptographic random usage
    random_string = "".join(random.choices(string.ascii_lowercase, k=6))  # noqa: S311

    migration_script.rev_id = f"{new_rev_id}{random_string}".zfill(12)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")

    if not url or url.strip() == "":
        url = DATABASE_URI

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        process_revision_directives=process_revision_directives,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    db_config = config.get_section(config.config_ini_section, {})
    if "sqlalchemy.url" not in db_config or not db_config["sqlalchemy.url"].strip():
        db_config["sqlalchemy.url"] = DATABASE_URI

    connectable = engine_from_config(
        db_config,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            process_revision_directives=process_revision_directives,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

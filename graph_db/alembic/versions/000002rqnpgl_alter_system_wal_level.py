"""alter system wal level

Revision ID: 000002rqnpgl
Revises: 000001hsgbpz
Create Date: 2025-04-19 09:57:28.872974

"""

from typing import Sequence, Union
from alembic import op
from sqlalchemy import text
from uuid import uuid4
import os


# revision identifiers, used by Alembic.
revision: str = "000002rqnpgl"
down_revision: Union[str, None] = "000001hsgbpz"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


POSTGRES_USER_DEBEZIUM_PASSWORD: str = os.getenv(
    "POSTGRES_USER_DEBEZIUM_PASSWORD", uuid4()
)


def upgrade():
    database = op.get_bind().execute(text("SELECT current_database()")).scalar()
    op.execute(
        f"""
        CREATE ROLE debezium_{database} REPLICATION LOGIN;
        ALTER ROLE debezium_{database} WITH PASSWORD '{POSTGRES_USER_DEBEZIUM_PASSWORD}';
        GRANT USAGE ON SCHEMA "public" TO debezium_{database};
        GRANT CREATE ON DATABASE {database} TO debezium_{database};
        """
    )
    op.execute(
        f"""
        CREATE ROLE debezium_{database}_replication_group;
        GRANT debezium_{database}_replication_group TO postgres;
        GRANT debezium_{database}_replication_group TO debezium_{database};
        """
    )
    op.execute(
        f"""
        ALTER TABLE document OWNER TO debezium_{database}_replication_group;
        """
    )


def downgrade():
    database = op.get_bind().execute(text("SELECT current_database()")).scalar()
    op.execute(
        """
        ALTER TABLE document OWNER TO postgres;
        """
    )
    op.execute(
        f"""
        DROP PUBLICATION IF EXISTS dbz_publication;
        DROP PUBLICATION IF EXISTS cdc;
        DROP ROLE IF EXISTS debezium_{database}_replication_group;
        """
    )
    op.execute(
        f"""
        REVOKE ALL PRIVILEGES ON SCHEMA public FROM debezium_{database};
        REVOKE CREATE ON DATABASE {database} FROM debezium_{database};
        DROP ROLE IF EXISTS debezium_{database};
        """
    )

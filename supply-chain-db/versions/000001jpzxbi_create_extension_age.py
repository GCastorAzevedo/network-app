"""create extension age

Revision ID: 000001jpzxbi
Revises:
Create Date: 2025-02-16 18:14:52.573287

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "000001jpzxbi"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS age;")

    op.execute("LOAD 'age';")

    op.execute('SET search_path = ag_catalog, "$user", public;')


def downgrade() -> None:
    op.execute("DROP EXTENSION age;")

    op.execute("RESET search_path;")

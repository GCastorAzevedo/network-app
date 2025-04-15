"""Create graph

Revision ID: 000004kqlgty
Revises: 000003bzoiva
Create Date: 2025-04-15 23:01:02.310330

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "000004kqlgty"
down_revision: Union[str, None] = "000003bzoiva"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(f""" SELECT * FROM ag_catalog.create_graph('main_grid'); """)


def downgrade() -> None:
    op.execute(f""" SELECT * FROM ag_catalog.drop_graph('main_grid', true); """)

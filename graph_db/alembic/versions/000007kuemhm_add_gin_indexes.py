"""Add GIN indexes

Revision ID: 000007kuemhm
Revises: 000006frfubq
Create Date: 2025-12-21 20:07:51.598919

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "000007kuemhm"
down_revision: Union[str, None] = "000006frfubq"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE INDEX idx_gin_unit_ancestors ON public.unit USING GIN (ancestors);
        """
    )

    op.execute(
        """
        CREATE INDEX idx_gin_unit_descendants ON public.unit USING GIN (descendants);
        """
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS public.idx_gin_unit_descendants;")
    op.execute("DROP INDEX IF EXISTS public.idx_gin_unit_ancestors;")

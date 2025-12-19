"""insert default relation

Revision ID: 000006frfubq
Revises: 000005mmwmou
Create Date: 2025-12-18 20:27:32.602004

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "000006frfubq"
down_revision: Union[str, None] = "000005mmwmou"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        INSERT INTO public.relation (name) VALUES ('links')
        ON CONFLICT (name) DO NOTHING;
        """
    )

    op.alter_column(
        "edge",
        "relation",
        existing_type=sa.String(),
        server_default="links",
        existing_nullable=False,
        schema="public",
    )


def downgrade() -> None:
    op.alter_column(
        "edge",
        "relation",
        existing_type=sa.String(),
        server_default=None,
        existing_nullable=False,
        schema="public",
    )

    # There is no simple way to undo the relation, so it is better to do it manually.
    # op.execute(
    #     """
    #     DELETE FROM public.relation WHERE name = 'links'
    #     """
    # )

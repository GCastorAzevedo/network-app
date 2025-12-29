"""Add user permissions

Revision ID: 000008xknril
Revises: 000007kuemhm
Create Date: 2025-12-29 17:43:15.113219

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "000008xknril"
down_revision: Union[str, None] = "000007kuemhm"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """ 
        ALTER TABLE public.unit ENABLE ROW LEVEL SECURITY;
        """
    )

    op.execute(
        """
        CREATE POLICY node_access ON public.unit
        FOR SELECT
        USING(
            ancestors && (SELECT nodes FROM app_users WHERE user_id = current_setting('app.current_user_id'))
        );
        """
    )

    op.create_table(
        "user",
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("nodes", postgresql.ARRAY(sa.Integer()), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column(
            "modified",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
        schema="public",
    )
    op.create_index(
        op.f("ix_public_user_nodes"), "user", ["nodes"], unique=False, schema="public"
    )


def downgrade() -> None:
    op.execute("DROP POLICY node_access ON public.unit;")
    op.execute("ALTER TABLE public.unit DISABLE ROW LEVEL SECURITY;")

    op.drop_index(op.f("ix_public_user_nodes"), table_name="user", schema="public")
    op.drop_table("user", schema="public")

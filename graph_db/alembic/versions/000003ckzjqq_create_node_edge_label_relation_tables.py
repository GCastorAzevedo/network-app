"""create node edge label relation tables

Revision ID: 000003ckzjqq
Revises: 000002rqnpgl
Create Date: 2025-04-19 09:59:12.514262

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "000003ckzjqq"
down_revision: Union[str, None] = "000002rqnpgl"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "label",
        sa.Column("name", sa.String(), nullable=False),
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
    op.create_table(
        "relation",
        sa.Column("name", sa.String(), nullable=False),
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
    op.create_table(
        "node",
        sa.Column("label", sa.String(), nullable=False),
        sa.Column(
            "properties", postgresql.JSONB(astext_type=sa.Text()), nullable=False
        ),
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
        sa.ForeignKeyConstraint(
            ["label"],
            ["public.label.name"],
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="public",
    )
    op.create_table(
        "edge",
        sa.Column("source_id", sa.Integer(), nullable=False),
        sa.Column("target_id", sa.Integer(), nullable=False),
        sa.Column("relation", sa.String(), nullable=False),
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
        sa.ForeignKeyConstraint(
            ["relation"],
            ["public.relation.name"],
        ),
        sa.ForeignKeyConstraint(["source_id"], ["public.node.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["target_id"], ["public.node.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("source_id", "target_id", "relation", name="uq_edge"),
        schema="public",
    )


def downgrade() -> None:
    op.drop_table("edge", schema="public")
    op.drop_table("node", schema="public")
    op.drop_table("relation", schema="public")
    op.drop_table("label", schema="public")

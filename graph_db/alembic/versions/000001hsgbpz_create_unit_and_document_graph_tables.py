"""create unit and document graph tables

Revision ID: 000001hsgbpz
Revises:
Create Date: 2025-04-19 09:51:35.985804

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "000001hsgbpz"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "unit",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=1000), nullable=True),
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
    )
    op.create_table(
        "document",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("unit_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=1000), nullable=True),
        sa.Column(
            "content",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="{}",
            nullable=False,
        ),
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
        sa.ForeignKeyConstraint(["unit_id"], ["unit.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_document_unit_id"), "document", ["unit_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_document_unit_id"), table_name="document")
    op.drop_table("document")
    op.drop_table("unit")

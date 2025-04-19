"""create unit table insert and delete triggers

Revision ID: 000004maadpm
Revises: 000003ckzjqq
Create Date: 2025-04-20 00:23:12.360363

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "000004maadpm"
down_revision: Union[str, None] = "000003ckzjqq"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE OR REPLACE FUNCTION insert_unit_node() RETURNS TRIGGER AS $$
            BEGIN
                INSERT INTO public.node (label, properties)
                VALUES (
                    'Unit',
                    jsonb_build_object(
                        'id', NEW.id
                    )
                );
                RETURN NEW;
            END;
        $$ LANGUAGE plpgsql;
        """
    )

    op.execute(
        """
        CREATE OR REPLACE TRIGGER insert_unit_node
        AFTER INSERT ON public.unit
        FOR EACH ROW
        EXECUTE FUNCTION insert_unit_node();
        """
    )

    op.execute(
        """
        CREATE OR REPLACE FUNCTION delete_unit_node() RETURNS TRIGGER AS $$
            BEGIN
                DELETE FROM public.node
                WHERE label = 'Unit' AND (properties ->> 'id')::int = New.id;
                RETURN OLD;
            END;
        $$ LANGUAGE plpgsql;
        """
    )

    op.execute(
        """
        CREATE OR REPLACE TRIGGER delete_unit_node
        AFTER DELETE ON public.unit
        FOR EACH ROW
        EXECUTE FUNCTION delete_unit_node();
        """
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS insert_unit_node ON public.unit;")
    op.execute("DROP FUNCTION IF EXISTS insert_unit_node;")

    op.execute("DROP TRIGGER IF EXISTS delete_unit_node ON public.unit;")
    op.execute("DROP FUNCTION IF EXISTS delete_unit_node;")

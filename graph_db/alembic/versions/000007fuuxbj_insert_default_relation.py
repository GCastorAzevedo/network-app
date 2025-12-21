"""insert default relation

Revision ID: 000007fuuxbj
Revises: 000006frfubq
Create Date: 2025-12-21 14:45:53.427668

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "000007fuuxbj"
down_revision: Union[str, None] = "000006frfubq"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# TODO: merge these definitions into alembic 5
# TODO: implement GIN indexes
def upgrade() -> None:
    op.execute(
        """
        CREATE OR REPLACE FUNCTION calculate_ancestors (node_id INT) RETURNS INTEGER[] AS $$
            BEGIN
                RETURN COALESCE(
                    (
                        WITH RECURSIVE ancestors(id) AS (
                            SELECT edge.source_id AS id FROM edge WHERE edge.target_id = node_id
                            UNION ALL
                            SELECT edge.source_id AS id FROM ancestors
                                JOIN edge ON ancestors.id = edge.target_id
                        ) SEARCH DEPTH FIRST BY id SET order_col CYCLE id SET is_cycle USING path
                        SELECT ARRAY_AGG(DISTINCT id) FROM ancestors
                    ),
                    ARRAY[]::INTEGER[]
                );
            END;
        $$ LANGUAGE plpgsql
        """
    )

    op.execute(
        """
        CREATE OR REPLACE FUNCTION calculate_descendants (node_id INT) RETURNS INTEGER[] AS $$
            BEGIN
                RETURN COALESCE(
                    (
                        WITH RECURSIVE descendants(id) AS (
                            SELECT edge.target_id AS id FROM edge WHERE edge.source_id = node_id
                            UNION ALL
                            SELECT edge.target_id AS id FROM descendants
                                JOIN edge ON descendants.id = edge.source_id
                        ) SEARCH DEPTH FIRST BY id SET order_col CYCLE id SET is_cycle USING PATH
                        SELECT ARRAY_AGG(DISTINCT id) FROM descendants
                    ),
                    ARRAY[]::INTEGER[]
                );
            END;
        $$ LANGUAGE plpgsql
        """
    )

    # op.execute(
    #     """
    #     CREATE OR REPLACE FUNCTION cascade_delete_node_on_unit_delete() RETURNS TRIGGER AS $$
    #         BEGIN
    #             -- DELETE FROM public.node
    #             -- WHERE id = OLD.node_id;

    #             --UPDATE unit
    #             --SET
    #             --    ancestors = calculate_ancestors(unit.node_id),
    #             --    descendants = calculate_descendants(unit.node_id)
    #             --WHERE OLD.node_id = ANY(unit.ancestors)
    #             --    OR OLD.node_id = ANY(unit.descendants);

    #             RETURN OLD;
    #         END;
    #     $$ LANGUAGE plpgsql;
    #     """
    # )

    # op.execute(
    #     """
    #     CREATE OR REPLACE TRIGGER cascade_delete_node_on_unit_delete
    #     BEFORE DELETE ON public.unit
    #     FOR EACH ROW
    #     EXECUTE FUNCTION cascade_delete_node_on_unit_delete();
    #     """
    # )

    # op.execute(
    #     """
    #     CREATE OR REPLACE TRIGGER cascade_delete_edge_on_node_delete
    #     BEFORE DELETE ON public.node
    #     FOR EACH ROW
    #     EXECUTE FUNCTION cascade_delete_edge_on_node_delete();
    #     """
    # )

    # op.execute(
    #     """
    #     CREATE OR REPLACE FUNCTION cascade_delete_edge_on_node_delete() RETURNS TRIGGER AS $$
    #         BEGIN
    #             DELETE FROM public.edge
    #             WHERE source_id = OLD.id OR target_id = OLD.id;

    #             UPDATE unit
    #             SET
    #                 ancestors = calculate_ancestors(unit.node_id),
    #                 descendants = calculate_descendants(unit.node_id)
    #             WHERE OLD.id = ANY(unit.ancestors)
    #                 OR OLD.id = ANY(unit.descendants);
    #             RETURN OLD;
    #         END;
    #     $$ LANGUAGE plpgsql
    #     """
    # )

    # op.execute(
    #     """
    #     CREATE OR REPLACE TRIGGER cascade_delete_edge_on_node_delete
    #     BEFORE DELETE ON public.node
    #     FOR EACH ROW
    #     EXECUTE FUNCTION cascade_delete_edge_on_node_delete();
    #     """
    # )

    # TODO: review the WHERE conditions
    op.execute(
        """
        CREATE OR REPLACE FUNCTION update_unit_tree_on_edge_delete() RETURNS TRIGGER AS $$
            BEGIN
                UPDATE unit
                SET
                    ancestors = calculate_ancestors(unit.node_id),
                    descendants = calculate_descendants(unit.node_id)
                WHERE OLD.source_id = ANY(unit.ancestors)
                    OR OLD.source_id = ANY(unit.descendants)
                    OR OLD.target_id = ANY(unit.ancestors)
                    OR OLD.target_id = ANY(unit.descendants);

                RETURN OLD;
            END;
        $$ LANGUAGE plpgsql;
        """
    )

    op.execute(
        """
        CREATE OR REPLACE TRIGGER update_unit_tree_on_edge_delete
        AFTER DELETE ON public.edge
        FOR EACH ROW
        EXECUTE FUNCTION update_unit_tree_on_edge_delete();
        """
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS update_unit_tree_on_edge_delete ON public.edge;")
    op.execute("DROP FUNCTION IF EXISTS update_unit_tree_on_edge_delete;")
    # op.execute(
    #     "DROP TRIGGER IF EXISTS cascade_delete_edge_on_node_delete ON public.node;"
    # )
    # op.execute("DROP FUNCTION IF EXISTS cascade_delete_edge_on_node_delete;")
    # op.execute(
    #     "DROP TRIGGER IF EXISTS cascade_delete_node_on_unit_delete ON public.unit;"
    # )
    # op.execute("DROP FUNCTION IF EXISTS cascade_delete_node_on_unit_delete;")
    op.execute("DROP FUNCTION IF EXISTS calculate_descendants;")
    op.execute("DROP FUNCTION IF EXISTS calculate_ancestors;")

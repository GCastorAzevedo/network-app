"""create unit tree on upsert trigger

Revision ID: 000005mmwmou
Revises: 000004maadpm
Create Date: 2025-12-09 07:43:54.155808

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "000005mmwmou"
down_revision: Union[str, None] = "000004maadpm"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_index("ix_document_unit_id", table_name="document")
    op.create_index(
        op.f("ix_public_document_unit_id"),
        "document",
        ["unit_id"],
        unique=False,
        schema="public",
    )
    op.drop_constraint("document_unit_id_fkey", "document", type_="foreignkey")
    op.create_foreign_key(
        "fk_document_unit_id",
        "document",
        "unit",
        ["unit_id"],
        ["id"],
        source_schema="public",
        referent_schema="public",
        ondelete="CASCADE",
    )
    op.drop_constraint("edge_relation_fkey", "edge", type_="foreignkey")
    op.drop_constraint("edge_target_id_fkey", "edge", type_="foreignkey")
    op.drop_constraint("edge_source_id_fkey", "edge", type_="foreignkey")
    op.create_foreign_key(
        "fk_edge_target_id",
        "edge",
        "node",
        ["target_id"],
        ["id"],
        source_schema="public",
        referent_schema="public",
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "fk_edge_source_id",
        "edge",
        "node",
        ["source_id"],
        ["id"],
        source_schema="public",
        referent_schema="public",
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "fk_edge_relation",
        "edge",
        "relation",
        ["relation"],
        ["name"],
        source_schema="public",
        referent_schema="public",
    )
    op.drop_constraint("node_label_fkey", "node", type_="foreignkey")
    op.create_foreign_key(
        "fk_node_label",
        "node",
        "label",
        ["label"],
        ["name"],
        source_schema="public",
        referent_schema="public",
    )
    op.add_column("unit", sa.Column("node_id", sa.Integer(), nullable=False))
    op.add_column(
        "unit", sa.Column("ancestors", postgresql.ARRAY(sa.Integer()), nullable=False)
    )
    op.add_column(
        "unit", sa.Column("descendants", postgresql.ARRAY(sa.Integer()), nullable=False)
    )
    op.create_index(
        op.f("ix_public_unit_ancestors"),
        "unit",
        ["ancestors"],
        unique=False,
        schema="public",
    )
    op.create_index(
        op.f("ix_public_unit_descendants"),
        "unit",
        ["descendants"],
        unique=False,
        schema="public",
    )
    op.create_index(
        op.f("ix_public_unit_node_id"),
        "unit",
        ["node_id"],
        unique=False,
        schema="public",
    )
    op.create_foreign_key(
        "fk_unit_node_id",
        "unit",
        "node",
        ["node_id"],
        ["id"],
        source_schema="public",
        referent_schema="public",
        ondelete="CASCADE",
    )

    op.execute(
        """
        CREATE OR REPLACE FUNCTION update_unit_tree_on_upsert() RETURNS TRIGGER AS $$
            DECLARE
                ancestors_arr INTEGER[];
                descendants_arr INTEGER[];
            BEGIN
                WITH RECURSIVE ancestors(id) AS (
                    SELECT edge.source_id AS id FROM edge WHERE edge.target_id = NEW.node_id
                    UNION ALL
                    SELECT edge.source_id AS id FROM ancestors
                        JOIN edge ON ancestors.id = edge.target_id
                    -- WHERE NOT EXISTS (SELECT 1 FROM ancestors WHERE id = e.source_id)
                    -- Do not specify 'SEARCH' method in case of depth first
                    -- SEARCH BREADTH FIRST BY id SET ordercol
                ) SEARCH DEPTH FIRST BY id SET order_col CYCLE id SET is_cycle USING path
                SELECT ARRAY_AGG(DISTINCT id) INTO ancestors_arr FROM ancestors;
                
                WITH RECURSIVE descendants(id) AS (
                    SELECT edge.target_id AS id FROM edge WHERE edge.source_id = NEW.node_id
                    UNION ALL
                    SELECT edge.target_id AS id FROM descendants
                        JOIN edge ON descendants.id = edge.source_id
                ) SEARCH DEPTH FIRST BY id SET order_col CYCLE id SET is_cycle USING path
                SELECT ARRAY_AGG(DISTINCT id) INTO descendants_arr FROM descendants;

                NEW.ancestors := COALESCE(ancestors_arr, ARRAY[]::INTEGER[]);
                NEW.descendants := COALESCE(descendants_arr, ARRAY[]::INTEGER[]);

                RETURN NEW;
            END;
        $$ LANGUAGE plpgsql;
        """
    )

    op.execute(
        """
        CREATE OR REPLACE TRIGGER update_unit_tree_on_upsert
        AFTER INSERT OR UPDATE ON public.unit
        FOR EACH ROW
        EXECUTE FUNCTION update_unit_tree_on_upsert();
        """
    )

    op.execute(
        """
        CREATE OR REPLACE FUNCTION update_unit_tree_on_edge_upsert() RETURNS TRIGGER AS $$
            BEGIN
                UPDATE unit
                SET
                    ancestors = (
                        WITH RECURSIVE ancestors(id) AS (
                            SELECT edge.source_id AS id FROM edge WHERE edge.target_id = unit.node_id
                            UNION ALL
                            SELECT edge.source_id AS id FROM ancestors
                                JOIN edge ON ancestors.id = edge.target_id
                        ) SEARCH DEPTH FIRST BY id SET order_col CYCLE id SET is_cycle USING path
                        SELECT ARRAY_AGG(DISTINCT id) AS ancestors
                    ),
                    descendants = (
                        WITH RECURSIVE descendants(id) AS (
                            SELECT edge.target_id AS id FROM edge WHERE edge.source_id = unit.node_id
                            UNION ALL
                            SELECT edge.target_id AS id FROM descendants
                                JOIN edge ON descendants.id = edge.source_id
                        ) SEARCH DEPTH FIRST BY id SET order_col CYCLE id SET is_cycle USING path
                        SELECT ARRAY_AGG(DISTINCT id) AS descendants
                    )
                    WHERE unit.node_id IN (NEW.source_id, NEW.target_id)
                        OR NEW.source_id = ANY(unit.ancestors)
                        OR NEW.target_id = ANY(unit.descendants);
        
                RETURN NEW;
            END;
        $$ LANGUAGE plpgsql
        """
    )

    op.execute(
        """
        CREATE OR REPLACE TRIGGER update_unit_tree_on_edge_upsert
        AFTER INSERT OR UPDATE ON public.edge
        FOR EACH ROW
        EXECUTE FUNCTION update_unit_tree_on_edge_upsert();
        """
    )

    op.execute("DROP TRIGGER IF EXISTS insert_unit_node ON public.unit;")
    op.execute("DROP FUNCTION IF EXISTS insert_unit_node;")

    op.execute("DROP TRIGGER IF EXISTS delete_unit_node ON public.unit;")
    op.execute("DROP FUNCTION IF EXISTS delete_unit_node;")


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS update_unit_tree_on_upsert ON public.unit;")
    op.execute("DROP FUNCTION IF EXISTS update_unit_tree_on_upsert;")
    op.execute("DROP TRIGGER IF EXISTS update_unit_tree_on_edge_upsert ON public.unit;")
    op.execute("DROP FUNCTION IF EXISTS update_unit_tree_on_edge_upsert;")

    op.drop_constraint("fk_unit_node_id", "unit", schema="public", type_="foreignkey")
    op.drop_index(op.f("ix_public_unit_node_id"), table_name="unit", schema="public")
    op.drop_index(
        op.f("ix_public_unit_descendants"), table_name="unit", schema="public"
    )
    op.drop_index(op.f("ix_public_unit_ancestors"), table_name="unit", schema="public")
    op.drop_column("unit", "descendants")
    op.drop_column("unit", "ancestors")
    op.drop_column("unit", "node_id")
    op.drop_constraint("fk_node_label", "node", schema="public", type_="foreignkey")
    op.create_foreign_key("node_label_fkey", "node", "label", ["label"], ["name"])
    op.drop_constraint("fk_edge_relation", "edge", schema="public", type_="foreignkey")
    op.drop_constraint("fk_edge_source_id", "edge", schema="public", type_="foreignkey")
    op.drop_constraint("fk_edge_target_id", "edge", schema="public", type_="foreignkey")
    op.create_foreign_key(
        "edge_source_id_fkey", "edge", "node", ["source_id"], ["id"], ondelete="CASCADE"
    )
    op.create_foreign_key(
        "edge_target_id_fkey", "edge", "node", ["target_id"], ["id"], ondelete="CASCADE"
    )
    op.create_foreign_key(
        "edge_relation_fkey", "edge", "relation", ["relation"], ["name"]
    )
    op.drop_constraint(
        "fk_document_unit_id", "document", schema="public", type_="foreignkey"
    )
    op.create_foreign_key(
        "document_unit_id_fkey",
        "document",
        "unit",
        ["unit_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.drop_index(
        op.f("ix_public_document_unit_id"), table_name="document", schema="public"
    )
    op.create_index("ix_document_unit_id", "document", ["unit_id"], unique=False)

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

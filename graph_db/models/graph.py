from graph_db.models.base import Base, EntityBase
from sqlalchemy import Column, Integer, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy import event, DDL
from sqlalchemy.dialects.postgresql import ARRAY


class Label(Base):
    __tablename__ = "label"
    __table_args__ = {"schema": "public"}

    name = Column(String, unique=True, nullable=False)

    nodes = relationship("Node", back_populates="node_label")


class Relation(Base):
    __tablename__ = "relation"
    __table_args__ = {"schema": "public"}

    name = Column(String, unique=True, nullable=False)

    edges = relationship("Edge", back_populates="edge_relation")


class Node(Base):
    __tablename__ = "node"
    __table_args__ = {"schema": "public"}

    label = Column(String, ForeignKey(Label.name), nullable=False)
    properties = Column(JSONB, nullable=False, default=dict)

    node_label = relationship("Label", back_populates="nodes")

    # TODO: delete or delete-orphan?
    outgoing_edges = relationship(
        "Edge",
        back_populates="source_node",
        foreign_keys="Edge.source_id",
        cascade="all, delete",
        passive_deletes=True,
    )

    incoming_edges = relationship(
        "Edge",
        back_populates="target_node",
        foreign_keys="Edge.target_id",
        cascade="all, delete",
        passive_deletes=True,
    )

    # TODO:?
    #     reachable = relationship(
    #         "ReachableNode",
    #         back_populates="node",
    #         uselist=False,
    #         cascade="all, delete",
    #     )

    #     documents = relationship(
    #         "Document",
    #         back_populates="node",
    #         cascade="all, delete-orphan",
    #     )
    units = relationship("Unit", back_populates="node", cascade="all, delete-orphan")

    def as_dict(self):
        return {"id": self.id, "label": self.label, "properties": self.properties}


# TODO: add tenant_id = Column(String(64), nullable=False, index=True)
class Unit(EntityBase):
    __tablename__ = "unit"
    __table_args__ = {"schema": "public"}

    node_id = Column(
        Integer,
        ForeignKey(Node.id, ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    ancestors = Column(ARRAY(Integer), nullable=False, default=list, index=True)
    descendants = Column(ARRAY(Integer), nullable=False, default=list, index=True)

    node = relationship("Node", back_populates="units")

    # TODO: deprecate
    documents = relationship(
        "Document", back_populates="unit", cascade="all, delete", passive_deletes=True
    )

    def as_dict(self):
        return {
            "id": self.id,
            "node_id": self.node_id,
            "name": self.name,
            "description": self.description,
            "ancestors": self.ancestors,
            "descendants": self.descendants,
        }


class Document(EntityBase):
    __tablename__ = "document"
    __table_args__ = {"schema": "public"}
    unit_id = Column(
        Integer, ForeignKey(Unit.id, ondelete="CASCADE"), index=True, nullable=False
    )
    content = Column(JSONB, nullable=False, server_default="{}")
    # TODO: add type? metadata? maybe a metadata table
    # type = Column(String(64), nullable=False, index=True)

    # TODO: node or unit?
    unit = relationship("Unit", back_populates="documents")

    def as_dict(self):
        return {
            "id": self.id,
            "unit_id": self.unit_id,
            "name": self.name,
            "description": self.description,
            "content": self.content,
        }


# TODO: deprecate or rename to Adjacency
class Edge(Base):
    __tablename__ = "edge"
    __table_args__ = (
        UniqueConstraint("source_id", "target_id", "relation", name="uq_edge"),
        {
            "schema": "public",
        },
    )

    # TODO: rename to from_id, to_id
    source_id = Column(Integer, ForeignKey(Node.id, ondelete="CASCADE"), nullable=False)
    target_id = Column(Integer, ForeignKey(Node.id, ondelete="CASCADE"), nullable=False)
    relation = Column(String, ForeignKey(Relation.name), nullable=False)

    edge_relation = relationship("Relation", back_populates="edges")
    source_node = relationship(
        "Node", foreign_keys=[source_id], back_populates="outgoing_edges"
    )
    target_node = relationship(
        "Node", foreign_keys=[target_id], back_populates="incoming_edges"
    )

    def as_dict(self):
        return {
            "id": self.id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relation": self.relation,
        }


# ============================================================================
# TRIGGER: Update unit ancestors/descendants when unit is upserted
# ============================================================================

update_unit_tree_on_upsert_function = DDL(
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


update_unit_tree_on_upsert_trigger = DDL(
    """
    CREATE OR REPLACE TRIGGER update_unit_tree_on_upsert
    AFTER INSERT OR UPDATE ON public.unit
    FOR EACH ROW
    EXECUTE FUNCTION update_unit_tree_on_upsert();
    """
)

update_unit_tree_on_edge_upsert_function = DDL(
    """
    CREATE OR REPLACE FUNCTION update_unit_tree_on_edge_upsert_function() RETURNS AS $$
        DECLARE
            ancestors_arr INTEGER[];
            descendants_arr INTEGER[];
        BEGIN
            FOR tree_node IN (
                SELECT node_id FROM unit
                WHERE NEW.source_id = ANY (unit.ancestors)
                    OR NEW.target_id = ANY (unit.descendants)
            ) LOOP  
                NEW.ancestors := COALESCE(ancestors_arr, ARRAY[]::INTEGER[]);
                NEW.descendants := COALESCE(descendants_arr, ARRAY[]::INTEGER[]);
            END LOOP;
            RETURN NEW;
        END;
    $$ LANGUAGE plpgsql
    """
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

event.listen(
    Unit.__table__,
    "after_create",
    update_unit_tree_on_upsert_function.execute_if(dialect="postgresql"),
)

event.listen(
    Unit.__table__,
    "after_create",
    update_unit_tree_on_upsert_trigger.execute_if(dialect="postgresql"),
)

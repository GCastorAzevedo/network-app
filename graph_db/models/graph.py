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
    #     # edges where this node is parent
    #     suppliers = relationship(
    #         "Adjacency",
    #         back_populates="from_node",
    #         foreign_keys="Adjacency.from_id",
    #         cascade="all, delete-orphan",
    #     )
    outgoing_edges = relationship(
        "Edge",
        back_populates="source_node",
        cascade="all, delete",
        passive_deletes=True,
    )
    #     # edges where this node is child
    #     customers = relationship(
    #         "Adjacency",
    #         back_populates="to_node",
    #         foreign_keys="Adjacency.to_id",
    #         cascade="all, delete",
    #     )
    incoming_edges = relationship(
        "Edge",
        back_populates="target_node",
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

    def as_dict(self):
        return {"id": self.id, "label": self.label, "properties": self.properties}


# TODO: add tenant_id = Column(String(64), nullable=False, index=True)
class Unit(EntityBase):
    __tablename__ = "unit"
    __table_args__ = {"schema": "public"}

    node_id = Column(
        Integer,
        ForeignKey(Node.id, ondelete="CASCADE"),
        primary_key=True,
        index=True,
        nullable=False,
    )
    ancestors = Column(ARRAY(Integer), nullable=False, default=list, index=True)
    descendants = Column(ARRAY(Integer), nullable=False, default=list, index=True)

    #
    # descendants = relationship(
    #     "Node",
    #     viewonly=True,
    #     order_by=path,
    #     primaryjoin=remote(foreign(path)).like(path.concat(".%")),
    # )

    # # Finding the ancestors is a little bit trickier. We need to create a fake
    # # secondary table since this behaves like a many-to-many join.
    # secondary = select(
    #     id.label("id"),
    #     func.unnest(
    #         cast(
    #             func.string_to_array(
    #                 func.regexp_replace(path, r"\.?\d+$", ""), "."
    #             ),
    #             ARRAY(Integer),
    #         )
    #     ).label("ancestor_id"),
    # ).alias()
    # ancestors = relationship(
    #     "Node",
    #     viewonly=True,
    #     secondary=secondary,
    #     primaryjoin=id == secondary.c.id,
    #     secondaryjoin=secondary.c.ancestor_id == id,
    #     order_by=path,
    # )
    #

    # node = relationship("Node", back_populates="reachable")
    unit = relationship("Node", back_populates="units")

    # TODO: deprecate
    documents = relationship(
        "Document", back_populates="unit", cascade="all, delete", passive_deletes=True
    )

    def as_dict(self):
        return {
            "id": self.id,
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
    source_id = Column(
        Integer,
        ForeignKey(Node.id, ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    target_id = Column(
        Integer,
        ForeignKey(Node.id, ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
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
# TRIGGER: Create unit node when unit is inserted
# ============================================================================
insert_graph_unit_node_function = DDL(
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

insert_graph_unit_node_trigger = DDL(
    """
    CREATE OR REPLACE TRIGGER insert_unit_node
    AFTER INSERT ON public.unit
    FOR EACH ROW
    EXECUTE FUNCTION insert_unit_node();
    """
)

event.listen(
    Unit.__table__,
    "after_create",
    insert_graph_unit_node_function.execute_if(dialect="postgresql"),
)

event.listen(
    Unit.__table__,
    "after_create",
    insert_graph_unit_node_trigger.execute_if(dialect="postgresql"),
)

# ============================================================================
# TRIGGER: Delete unit node when unit is deleted
# ============================================================================
delete_graph_unit_node_function = DDL(
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

delete_graph_unit_node_trigger = DDL(
    """
    CREATE OR REPLACE TRIGGER delete_unit_node
    AFTER DELETE ON public.unit
    FOR EACH ROW
    EXECUTE FUNCTION delete_unit_node();
    """
)

event.listen(
    Unit.__table__,
    "after_create",
    delete_graph_unit_node_function.execute_if(dialect="postgresql"),
)

event.listen(
    Unit.__table__,
    "after_create",
    delete_graph_unit_node_trigger.execute_if(dialect="postgresql"),
)

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
            WITH RECURSIVE ancestors AS (
                SELECT edges.source_id AS id FROM edges WHERE edges.target_id = NEW.node_id
                UNION ALL
                SELECT edges.source_id AS id FROM ancestors
                    JOIN edges ON ancestors.id = edge.target_id
                -- WHERE NOT EXISTS (SELECT 1 FROM ancestors WHERE id = e.source_id)
            )
            CYCLE id SET is_cycle TO true DEFAULT false
            SELECT ARRAY_AGG(DISTINCT id) INTO ancestors_arr FROM ancestors;
            
            WITH RECURSIVE descendants AS (
                SELECT edges.target_id AS id FROM edges WHERE edges.source_id = NEW.node_id
                UNION ALL
                SELECT edges.target_id AS id FROM descendants
                    JOIN edges ON descendants.id = edges.source_id
                -- WHERE NOT EXISTS (SELECT 1 FROM descendants WHERE id = e.target_id)
            )
            CYCLE id SET is_cycle TO true DEFAULT false
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

# ##########################################################################
# TODO: ####################################################################

# from sqlalchemy import Column, Integer, String, JSON
# from sqlalchemy.sql import func
# from sqlalchemy import ForeignKey, TIMESTAMP
# from sqlalchemy.orm import relationship, DeclarativeBase
# from sqlalchemy.dialects.postgresql import ARRAY


# class Base(DeclarativeBase):
#     pass


# NAME_MAX_LENGTH = 100
# DESCRIPTION_MAX_LENGTH = 1000


# class Node(Base):
#     __tablename__ = "nodes"
#     __table_args__ = {"schema": "public"}

#     id = Column(Integer, primary_key=True)
#     tenant_id = Column(String(64), nullable=False, index=True)
#     name = Column(String(NAME_MAX_LENGTH), nullable=False)
#     description = Column(String(DESCRIPTION_MAX_LENGTH))
#     properties = Column(JSON, nullable=True)

#     created = Column(TIMESTAMP(timezone=True), server_default=func.now())
#     modified = Column(
#         TIMESTAMP(timezone=True),
#         server_default=func.now(),
#         onupdate=func.now(),
#     )

#     # edges where this node is parent
#     suppliers = relationship(
#         "Adjacency",
#         back_populates="from_node",
#         foreign_keys="Adjacency.from_id",
#         cascade="all, delete-orphan",
#     )

#     # edges where this node is child
#     customers = relationship(
#         "Adjacency",
#         back_populates="to_node",
#         foreign_keys="Adjacency.to_id",
#         cascade="all, delete",
#     )

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


# class Adjacency(Base):
#     __tablename__ = "adjacency"
#     __table_args__ = {"schema": "public"}

#     from_id = Column(
#         Integer,
#         ForeignKey("public.nodes.id", ondelete="CASCADE"),
#         primary_key=True,
#     )
#     to_id = Column(
#         Integer,
#         primary_key=True,
#     )
#     tenant_id = Column(String(64), nullable=False, index=True)

#     created = Column(TIMESTAMP(timezone=True), server_default=func.now())
#     modified = Column(
#         TIMESTAMP(timezone=True),
#         server_default=func.now(),
#         onupdate=func.now(),
#     )

#     from_node = relationship("Node", back_populates="suppliers", foreign_keys=[from_id])
#     to_node = relationship("Node", back_populates="customers", foreign_keys=[to_id])


# class ReachableNode(Base):
#     __tablename__ = "reachable_nodes"
#     __table_args__ = {"schema": "public"}

#     node_id = Column(
#         Integer,
#         ForeignKey("public.nodes.id", ondelete="CASCADE"),
#         primary_key=True,
#     )
#     tenant_id = Column(String(64), nullable=False, primary_key=True, index=True)

#     ancestors = Column(ARRAY(Integer), nullable=False, default=list, index=False)
#     children = Column(ARRAY(Integer), nullable=False, default=list, index=False)

#     created = Column(TIMESTAMP(timezone=True), server_default=func.now())
#     modified = Column(
#         TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now()
#     )

#     node = relationship("Node", back_populates="reachable")


# class Document(Base):
#     __tablename__ = "documents"
#     __table_args__ = {"schema": "public"}

#     document_id = Column(Integer, primary_key=True)
#     tenant_id = Column(String(64), nullable=False, index=True)

#     node_id = Column(
#         Integer,
#         ForeignKey("public.nodes.id", ondelete="CASCADE"),
#         nullable=False,
#         index=True,
#     )

#     type = Column(String(64), nullable=False, index=True)
#     content = Column(JSON, nullable=False)

#     created = Column(TIMESTAMP(timezone=True), server_default=func.now())
#     modified = Column(
#         TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now()
#     )

#     node = relationship("Node", back_populates="documents")


# class UserAllowedNode(Base):
#     __tablename__ = "users_allowed_nodes"
#     __table_args__ = {"schema": "public"}

#     user_id = Column(String(128), primary_key=True)
#     tenant_id = Column(String(64), nullable=False, primary_key=True, index=True)

#     allowed_roots = Column(ARRAY(Integer), nullable=False, default=list)

#     created = Column(TIMESTAMP(timezone=True), server_default=func.now())
#     modified = Column(
#         TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now()
#     )

# ##########################################################################

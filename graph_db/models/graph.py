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
    outgoing_edges = relationship(
        "Edge",
        back_populates="source_node",
        cascade="all, delete",
        passive_deletes=True,
    )
    incoming_edges = relationship(
        "Edge",
        back_populates="target_node",
        cascade="all, delete",
        passive_deletes=True,
    )

    def as_dict(self):
        return {"id": self.id, "label": self.label, "properties": self.properties}


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
    children = Column(ARRAY(Integer), nullable=False, default=list, index=True)

    unit = relationship("Node", back_populates="units")

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

    documents = relationship(
        "Document", back_populates="unit", cascade="all, delete", passive_deletes=True
    )

    def as_dict(self):
        return {"id": self.id, "name": self.name, "description": self.description}


class Document(EntityBase):
    __tablename__ = "document"
    __table_args__ = {"schema": "public"}
    unit_id = Column(
        Integer, ForeignKey(Unit.id, ondelete="CASCADE"), index=True, nullable=False
    )
    content = Column(JSONB, nullable=False, server_default="{}")

    unit = relationship("Unit", back_populates="documents")

    def as_dict(self):
        return {
            "id": self.id,
            "unit_id": self.unit_id,
            "name": self.name,
            "description": self.description,
            "content": self.content,
        }


# TODO: deprecate
class Edge(Base):
    __tablename__ = "edge"
    __table_args__ = (
        UniqueConstraint("source_id", "target_id", "relation", name="uq_edge"),
        {
            "schema": "public",
        },
    )

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


# Trigger: create unit node
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

# Trigger: delete unit node
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

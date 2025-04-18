from graph_db.models.base import Base, EntityBase
from sqlalchemy import Column, Integer, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy import event, DDL


class Unit(EntityBase):
    __tablename__ = "unit"
    __table_args__ = {"schema": "public"}

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


# #############################################################################################

# from sqlalchemy import event, DDL

# create_graph_node_function = DDL(
#     "CREATE FUNCTION add_node() RETURNS TRIGGER AS $$ "
#     "BEGIN NEW.data := 'ins'; "
#     "RETURN NEW; "
#     "END; $$ LANGUAGE PLPGSQL"
# )

# update_graph_node_function = DDL("CREATE FUNCTION update_node() RETURNS TRIGGER AS $$ ")

# delete_graph_node_function = DDL("CREATE FUNCTION delete_node() RETURNS TRIGGER AS $$ ")

# create_graph_node_trigger = DDL("CREATE TRIGGER dt_ins AFTER INSERT ON document ")

# update_graph_node_trigger = DDL("CREATE TRIGGER dt_ins AFTER UPDATE ON document ")

# delete_graph_node_trigger = DDL("CREATE TRIGGER dt_ins AFTER DELETE ON document ")

# event.listen(
#     Document.__table__,
#     "after_create",
#     create_graph_node_function.execute_if(dialect="postgresql"),
# )
# event.listen(
#     Document.__table__,
#     "after_update",
#     update_graph_node_function.execute_if(dialect="postgresql"),
# )
# event.listen(
#     Document.__table__,
#     "after_delete",
#     delete_graph_node_function.execute_if(dialect="postgresql"),
# )

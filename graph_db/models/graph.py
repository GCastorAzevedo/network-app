from graph_db.models.base import Base
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy import DDL


class Unit(Base):
    __tablename__ = "unit"

    documents = relationship(
        "Document", back_populates="unit", cascade="all, delete", passive_deletes=True
    )


class Document(Base):
    __tablename__ = "document"
    unit_id = Column(
        Integer, ForeignKey(Unit.id, ondelete="CASCADE"), index=True, nullable=False
    )
    content = Column(JSONB, nullable=False, server_default="{}")

    unit = relationship("Unit", back_populates="documents")


create_graph_node_function = DDL(
    "CREATE FUNCTION add_node() RETURNS TRIGGER AS $$ "
    "BEGIN NEW.data := 'ins'; "
    "RETURN NEW; "
    "END; $$ LANGUAGE PLPGSQL"
)

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

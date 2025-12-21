from graph_db.models import graph
from graph_db.session import get_sync_session
from sqlalchemy import select, delete, update, insert
from graph_api.api.v1.graphql.types import Document, Edge, Unit
from graph_api.api.v1.graphql.models import (
    AddDocumentInput,
    UpdateDocumentInput,
    AddUnitInput,
    AddEdgeInput,
    UpdateUnitInput,
)


async def get_units() -> list[Unit]:
    session = get_sync_session()
    sql = select(graph.Unit).order_by(graph.Unit.name)
    db_units = session.execute(sql).scalars().unique().all()
    return [Unit(**unit.as_dict()) for unit in db_units]


async def get_unit_by_id(id: int) -> Unit:
    session = get_sync_session()
    sql = select(graph.Unit).where(graph.Unit.id == id)
    db_units = session.execute(sql).scalars().unique().all()
    return Unit(**db_units[0].as_dict())


async def add_unit(input: AddUnitInput) -> Unit:
    session = get_sync_session()
    node = graph.Node(label="Unit", properties={"unit_name": input.name})
    session.add(node)
    session.flush()

    sql = (
        insert(graph.Unit)
        .values(node_id=node.id, **input.model_dump(exclude_none=True))
        .returning(graph.Unit)
    )
    db_units = session.execute(sql).scalars().unique().all()
    session.commit()
    return Unit(**db_units[0].as_dict())


async def update_unit(input: UpdateUnitInput) -> Unit:
    session = get_sync_session()
    sql = (
        update(graph.Unit)
        .where(graph.Unit.id == input.id)
        .values(**input.model_dump(exclude_none=True, exclude={"id"}))
        .returning(graph.Unit)
    )
    db_units = session.execute(sql).scalars().unique().all()
    session.commit()
    return Unit(**db_units[0].as_dict())


async def delete_unit(id: int) -> Unit:
    # TODO: add comment and/or change resolver name
    session = get_sync_session()
    unit_sql = select(graph.Unit).where(graph.Unit.id == id)
    db_unit = session.execute(unit_sql).scalars().unique().all()
    if not db_unit:
        raise ValueError(f"Unit with id {id} not found.")
    unit = Unit(**db_unit[0].as_dict())

    delete_sql = delete(graph.Node).where(graph.Node.id == unit.node_id)
    session.execute(delete_sql)
    session.commit()

    return unit


async def get_edges() -> list[Edge]:
    session = get_sync_session()
    sql = select(graph.Edge).order_by(graph.Edge.source_id, graph.Edge.target_id)
    db_edges = session.execute(sql).scalars().unique().all()
    return [
        Edge(
            id=edge.id,
            source_unit_id=edge.source_id,
            target_unit_id=edge.target_id,
        )
        for edge in db_edges
    ]


async def add_edge(input: AddEdgeInput) -> Edge:
    session = get_sync_session()
    sql = select(graph.Unit.id, graph.Unit.node_id).where(
        graph.Unit.id.in_([input.source_unit_id, input.target_unit_id])
    )
    units = {id: node_id for id, node_id in session.execute(sql).all()}
    if len(units) != 2:
        raise ValueError("Source or target not found")

    edge = graph.Edge(
        source_id=units[input.source_unit_id], target_id=input.target_unit_id
    )
    session.add(edge)
    session.commit()
    return Edge(
        id=edge.id,
        source_unit_id=input.source_unit_id,
        target_unit_id=input.target_unit_id,
    )


async def delete_edge(id: int) -> Edge:
    session = get_sync_session()
    sql = delete(graph.Edge).where(graph.Edge.id == id).returning(graph.Edge)
    db_edges = session.execute(sql).scalars().unique().all()
    session.commit()
    return Edge(**db_edges[0].as_dict())


async def get_documents() -> list[Document]:
    session = get_sync_session()
    sql = select(graph.Document).order_by(graph.Document.name)
    db_documents = session.execute(sql).scalars().unique().all()
    return [Document(**unit.as_dict()) for unit in db_documents]


async def get_document_by_id(id: int) -> Document:
    session = get_sync_session()
    sql = select(graph.Document).where(graph.Document.id == id)
    db_documents = session.execute(sql).scalars().unique().all()
    return Document(**db_documents[0].as_dict())


async def add_document(input: AddDocumentInput) -> Document:
    session = get_sync_session()
    sql = (
        insert(graph.Document)
        .values(**input.model_dump(exclude_none=True))
        .returning(graph.Document)
    )
    db_documents = session.execute(sql).scalars().unique().all()
    session.commit()
    return Document(**db_documents[0].as_dict())


async def update_document(input: UpdateDocumentInput) -> Document:
    session = get_sync_session()
    sql = (
        update(graph.Document)
        .where(graph.Document.id == input.id)
        .values(**input.model_dump(exclude_none=True, exclude={"id"}))
        .returning(graph.Document)
    )
    db_documents = session.execute(sql).scalars().unique().all()
    session.commit()
    return Document(**db_documents[0].as_dict())


async def delete_document(id: int) -> Document:
    session = get_sync_session()
    sql = (
        delete(graph.Document).where(graph.Document.id == id).returning(graph.Document)
    )
    db_documents = session.execute(sql).scalars().unique().all()
    session.commit()
    return Document(**db_documents[0].as_dict())

from graph_db.models import graph
from graph_db.session import get_sync_session
from sqlalchemy import select, delete, update, insert
from graph_api.api.v1.graphql.types import Document, Unit
from graph_api.api.v1.graphql.models import (
    AddDocumentInput,
    UpdateDocumentInput,
    AddUnitInput,
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
    sql = (
        insert(graph.Unit)
        .values(**input.model_dump(exclude_none=True))
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
    session = get_sync_session()
    sql = delete(graph.Unit).where(graph.Unit.id == id).returning(graph.Unit)
    db_units = session.execute(sql).scalars().unique().all()
    session.commit()
    return Unit(**db_units[0].as_dict())


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

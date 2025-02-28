from graph_db.models import graph
from graph_db.session import get_sync_session
from sqlalchemy import select, delete, update, insert
from graph_api.api.v1.graphql.types import Document, Unit


async def get_units() -> list[Unit]:
    session = get_sync_session()
    sql = select(graph.Unit).order_by(graph.Unit.name)
    db_units = session.execute(sql).scalars().unique().all()
    return [Unit(**unit.as_dict()) for unit in db_units]


async def add_unit(name: str, description: str) -> Unit:
    session = get_sync_session()
    sql = (
        insert(graph.Unit)
        .values(name=name, description=description)
        .returning(graph.Unit)
    )
    db_units = session.execute(sql).scalars().unique().all()
    return [Unit(**unit.as_dict()) for unit in db_units][0]


async def update_unit(id: int, name: str, description: str) -> Unit:
    session = get_sync_session()
    sql = (
        update(graph.Unit)
        .where(graph.Unit.id == id)
        .values(name=name, description=description)
        .returning(graph.Unit)
    )
    db_units = session.execute(sql).scalars().unique().all()
    return [Unit(**unit.as_dict()) for unit in db_units][0]


async def delete_unit(id: int) -> Unit:
    session = get_sync_session()
    sql = delete(graph.Unit).where(graph.Unit.id == id).returning(graph.Unit)
    db_units = session.execute(sql).scalars().unique().all()
    return [Unit(**unit.as_dict()) for unit in db_units][0]


async def get_documents() -> list[Document]:
    session = get_sync_session()
    sql = select(graph.Document).order_by(graph.Document.name)
    db_documents = session.execute(sql).scalars().unique().all()
    return [Document(**unit.as_dict()) for unit in db_documents]

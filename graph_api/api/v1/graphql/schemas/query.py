import strawberry
from graph_api.api.v1.graphql.types import Document, Edge, Unit
from graph_api.api.v1.graphql.resolvers import (
    get_units,
    get_documents,
    get_edges,
    get_unit_by_id,
    get_document_by_id,
)


@strawberry.type
class Query:
    @strawberry.field
    async def unit(self, id: int) -> Unit:
        return await get_unit_by_id(id)

    @strawberry.field
    async def units(self) -> list[Unit]:
        return await get_units()

    @strawberry.field
    async def document(self, id: int) -> Document:
        return await get_document_by_id(id)

    @strawberry.field
    async def documents(self) -> list[Document]:
        return await get_documents()

    @strawberry.field
    async def edges(self) -> list[Edge]:
        return await get_edges()

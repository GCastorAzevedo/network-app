import strawberry
from graph_api.api.v1.graphql.types import Document, Unit
from graph_api.api.v1.graphql.resolvers import get_units, get_documents


@strawberry.type
class Query:
    @strawberry.field
    async def units(self) -> list[Unit]:
        return await get_units()

    @strawberry.field
    async def documents(self) -> list[Document]:
        return await get_documents()

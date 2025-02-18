import strawberry
from strawberry.fastapi import GraphQLRouter


@strawberry.type
class Query:
    @strawberry.field
    async def hello(self) -> str:
        return "Hello World"


schema = strawberry.Schema(query=Query)

graphql_router = GraphQLRouter(schema)

import strawberry
from strawberry.fastapi import GraphQLRouter

from graph_api.api.v1.graphql.schemas.query import Query
from graph_api.api.v1.graphql.schemas.mutation import Mutation

schema = strawberry.Schema(query=Query, mutation=Mutation)

graphql_router = GraphQLRouter(schema)

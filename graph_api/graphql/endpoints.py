import strawberry
from strawberry.fastapi import GraphQLRouter

from graph_api.graphql.schemas.query import Query
from graph_api.graphql.schemas.mutation import Mutation

schema = strawberry.Schema(query=Query, mutation=Mutation)

graphql_router = GraphQLRouter(schema)

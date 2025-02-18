from fastapi import APIRouter

from graph_api.api.v1.graph.endpoints import route as wholly_graph_route
from graph_api.api.v1.graphql.endpoints import graphql_router

route = APIRouter()

route.include_router(wholly_graph_route, prefix="/whollygrid", tags=["graph"])
route.include_router(graphql_router, prefix="/graphql", tags=["graph"])

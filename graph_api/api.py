from fastapi import APIRouter

from graph_api.graphql.endpoints import graphql_router
from graph_api.authentication import route as auth_router

route = APIRouter()

route.include_router(graphql_router, prefix="/graphql", tags=["graph"])
route.include_router(auth_router, prefix="/auth", tags=["graph"])

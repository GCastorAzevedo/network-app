from fastapi import APIRouter

from graph_api.api.v1.graph.endpoints import route as wholly_graph_route

route = APIRouter()

route.include_router(wholly_graph_route, prefix="/whollygraph", tags=["graph"])

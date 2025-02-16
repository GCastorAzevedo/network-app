from fastapi import APIRouter

from supply_chain_api.api.v1.supply_chain.endpoints import route as supply_chain_route

route = APIRouter()

route.include_router(supply_chain_route, prefix="/supply_chain", tags=["supply_chain"])

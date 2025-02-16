from fastapi import FastAPI

from supply_chain_api.api.v1.api import route as api_v1_route

app = FastAPI(docs_url="/docs", openapi_url="/docs/openapi.json")

app.include_router(api_v1_route, prefix="/v1")

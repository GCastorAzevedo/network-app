from fastapi import FastAPI

from api.v1.api import route as api_v1_route

app = FastAPI()

app.include_router(api_v1_route, prefix="/v1")

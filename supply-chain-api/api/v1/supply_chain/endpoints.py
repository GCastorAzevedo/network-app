from fastapi import APIRouter

route = APIRouter()


@route.get("/")
def read_root():
    return {"Hello": "World"}

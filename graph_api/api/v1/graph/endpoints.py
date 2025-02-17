from fastapi import APIRouter
from sqlalchemy import text
from graph_db.session import DBSession

route = APIRouter()


@route.get("/")
def read_root(session: DBSession):
    results = session.execute(text("SELECT 1")).scalar()
    return {"results": results}

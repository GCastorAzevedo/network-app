from typing import Iterator
from common.config import settings
from fastapi import Depends
from typing_extensions import Annotated
from sqlalchemy.orm.session import Session
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

engine: Engine = create_engine(str(settings.DATABASE_URI), pool_pre_ping=True)
SessionMaker = sessionmaker(bind=engine, expire_on_commit=False)


def get_db_session() -> Iterator[Session]:
    session: Session = SessionMaker()

    try:
        yield session
    finally:
        session.close()


DBSession = Annotated[Session, Depends(get_db_session)]

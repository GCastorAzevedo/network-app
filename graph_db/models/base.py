from sqlalchemy import Column, Integer, TIMESTAMP, String
from datetime import datetime, timezone
from sqlalchemy.sql import func
from sqlalchemy.orm import DeclarativeBase


NAME_MAX_LENGTH = 100
DESCRIPTION_MAX_LENGTH = 1000


class Base(DeclarativeBase):
    id = Column(Integer, primary_key=True)
    name = Column(String(NAME_MAX_LENGTH), nullable=False)
    description = Column(String(DESCRIPTION_MAX_LENGTH))
    created = Column(TIMESTAMP(timezone=True), server_default=func.now())
    modified = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=datetime.now(timezone.utc),
    )

    # TODO: Add a method to get by ID


class GraphBase(DeclarativeBase):
    id = Column(Integer, primary_key=True)
    created = Column(TIMESTAMP(timezone=True), server_default=func.now())
    modified = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=datetime.now(timezone.utc),
    )

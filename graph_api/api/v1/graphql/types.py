import strawberry
from typing import Optional


@strawberry.type
class Unit:
    id: int
    name: Optional[str] = None


@strawberry.type
class Document:
    id: int
    name: Optional[str] = None

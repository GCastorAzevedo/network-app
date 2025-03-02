import strawberry
from typing import Optional, NewType


JSON = strawberry.scalar(
    NewType("JSON", object),
    description="The `JSON` scalar represents JSON values as specified by ECMA-404",
    serialize=lambda v: v,
    parse_value=lambda v: v,
)


@strawberry.type
class Unit:
    id: int
    name: Optional[str] = None
    description: Optional[str] = None


@strawberry.type
class Document:
    id: int
    unit_id: int
    name: Optional[str] = None
    description: Optional[str] = None
    content: JSON

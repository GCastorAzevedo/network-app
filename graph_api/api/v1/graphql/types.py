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
    node_id: int
    name: Optional[str] = None
    description: Optional[str] = None
    ancestors: list[int] = strawberry.field(default_factory=list)
    descendants: list[int] = strawberry.field(default_factory=list)


@strawberry.type
class Edge:
    id: int
    target_unit_id: int
    source_unit_id: int


@strawberry.type
class Document:
    id: int
    unit_id: int
    name: Optional[str] = None
    description: Optional[str] = None
    content: JSON

from typing import Optional
from pydantic import BaseModel


# TODO: check the page https://strawberry.rocks/docs/integrations/pydantic
class AddDocumentInput(BaseModel):
    unit_id: int
    name: str
    description: str | None = None
    content: dict | None = None


class UpdateDocumentInput(BaseModel):
    id: int
    name: str | None = None
    description: str | None = None
    content: dict | None = None


class AddUnitInput(BaseModel):
    name: str | None = None
    description: str | None = None


class UpdateUnitInput(BaseModel):
    id: int
    name: str | None = None
    description: str | None = None


class AddEdgeInput(BaseModel):
    target_unit_id: int
    source_unit_id: int

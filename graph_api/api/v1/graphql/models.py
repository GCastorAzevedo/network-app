from typing import Optional
from pydantic import BaseModel


class AddDocumentInput(BaseModel):
    unit_id: int
    name: str
    description: Optional[str] = None
    content: Optional[dict] = None


class UpdateDocumentInput(BaseModel):
    id: int
    name: Optional[str] = None
    description: Optional[str] = None
    content: Optional[dict] = None


class AddUnitInput(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class UpdateUnitInput(BaseModel):
    id: int
    name: Optional[str] = None
    description: Optional[str] = None

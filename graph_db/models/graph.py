from graph_db.models.base import Base
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship


class Unit(Base):
    __tablename__ = "unit"

    documents = relationship(
        "Document", back_populates="unit", cascade="all, delete", passive_deletes=True
    )


class Document(Base):
    __tablename__ = "document"
    unit_id = Column(
        Integer, ForeignKey(Unit.id, ondelete="CASCADE"), index=True, nullable=False
    )
    content = Column(JSONB, nullable=False, server_default="{}")

    unit = relationship("Unit", back_populates="documents")

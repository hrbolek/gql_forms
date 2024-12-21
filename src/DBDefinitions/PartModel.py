import uuid
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .BaseModel import BaseModel, UUIDFKey

class PartModel(BaseModel):
    """Model representing a part of a form."""

    __tablename__ = "formparts"

    name: Mapped[str] = mapped_column(String, nullable=True, default=None, comment="Name of the part")
    name_en: Mapped[str] = mapped_column(String, nullable=True, default=None, comment="English name of the part")
    order: Mapped[int] = mapped_column(Integer, nullable=True, default=None, comment="Order in the parent entity")
    
    section_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("formsections.id"), 
        index=True, 
        nullable=True, 
        default=None, 
        comment="Foreign key to the form section"
    )
    
    state_id: Mapped[uuid.UUID] = UUIDFKey(nullable=True, comment="State of the request")
    
    # Relationships
    section: Mapped["SectionModel"] = relationship(
        "SectionModel", 
        back_populates="parts", 
        default=None, 
        uselist=False
    )
    items: Mapped[list["ItemModel"]] = relationship(
        "ItemModel", 
        back_populates="part", 
        default_factory=list,
        uselist=True
    )

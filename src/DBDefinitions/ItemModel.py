import uuid
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .BaseModel import BaseModel, UUIDFKey

class ItemModel(BaseModel):
    """Model representing an item in a form."""

    __tablename__ = "formitems"

    name: Mapped[str] = mapped_column(String, nullable=True, default=None, comment="Name of the value")
    name_en: Mapped[str] = mapped_column(String, nullable=True, default=None, comment="English name of the value")
    
    order: Mapped[int] = mapped_column(Integer, nullable=True, default=None, comment="Order in the parent entity")
    value: Mapped[str] = mapped_column(String, nullable=True, default=None, comment="Item value, together with name it is named value")
    
    part_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("formparts.id"), index=True, nullable=True, default=None, comment="Foreign key to the form part")
    type_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("formitemtypes.id"), index=True, nullable=True, default=None, comment="Foreign key to the item type")
    
    state_id: Mapped[uuid.UUID] = UUIDFKey(nullable=True, comment="State of the request")
    
    # Relationships
    part: Mapped["PartModel"] = relationship(
        "PartModel", 
        back_populates="items", 
        default=None, 
        uselist=False
    )
    type: Mapped["ItemTypeModel"] = relationship(
        "ItemTypeModel", 
        back_populates="items", 
        default=None, 
        uselist=False
    )

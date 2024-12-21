import uuid
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .BaseModel import BaseModel

class ItemTypeModel(BaseModel):
    """Model representing a type of form item."""

    __tablename__ = "formitemtypes"

    name: Mapped[str] = mapped_column(String, nullable=True, default=None, comment="Name of the type")
    name_en: Mapped[str] = mapped_column(String, nullable=True, default=None, comment="English name of the type")
    
    query: Mapped[str] = mapped_column(String, nullable=True, default=None, comment="API query associated with the item type (e.g., `/students/%`)")
    selector: Mapped[str] = mapped_column(String, nullable=True, default=None, comment="Selector for picking the right value from the query (e.g., `result;item;id`)")
    
    category_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("formitemcategories.id"), 
        index=True, 
        nullable=True, 
        default=None, 
        comment="Foreign key to item category"
    )
    
    # Relationships
    items: Mapped[list["ItemModel"]] = relationship(
        "ItemModel", 
        back_populates="type", 
        default_factory=list,
        uselist=True
    )
    category: Mapped["ItemCategoryModel"] = relationship(
        "ItemCategoryModel", 
        back_populates="types", 
        default=None, 
        uselist=False
    )

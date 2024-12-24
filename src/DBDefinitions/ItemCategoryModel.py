import uuid
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .BaseModel import BaseModel

class ItemCategoryModel(BaseModel):
    """Model representing a category for form items."""

    __tablename__ = "formitemcategories"

    name: Mapped[str] = mapped_column(String, nullable=True, default=None, comment="Name of the category")
    name_en: Mapped[str] = mapped_column(String, nullable=True, default=None, comment="English name of the category")
    
    # Relationships
    types = relationship(
        "ItemTypeModel", 
        back_populates="category", 
        default_factory=list,
        uselist=True
    )

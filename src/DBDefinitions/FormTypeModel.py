import uuid
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .BaseModel import BaseModel

class FormTypeModel(BaseModel):
    """Model representing a form type."""

    __tablename__ = "formtypes"

    name: Mapped[str] = mapped_column(String, nullable=True, default=None, comment="Name of the type")
    name_en: Mapped[str] = mapped_column(String, nullable=True, default=None, comment="English name of the type")
    
    category_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("formcategories.id"), 
        index=True, 
        nullable=True, 
        default=None, 
        comment="Foreign key to form categories"
    )
    
    # Relationships
    forms: Mapped[list["FormModel"]] = relationship(
        "FormModel", 
        back_populates="type", 
        default_factory=list,
        uselist=True
    )
    category: Mapped["FormCategoryModel"] = relationship(
        "FormCategoryModel", 
        back_populates="types",
        default=None, 
    )
